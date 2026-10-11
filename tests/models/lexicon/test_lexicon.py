# SPDX-FileCopyrightText: 2026 HanYang06
# SPDX-License-Identifier: Apache-2.0

"""词表：初始化 / 寻址 / 固化 / 配置接线。"""

from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from lna.models.lexicon import Lexicon, hex_to_id, id_to_hex


DIM = 8
V_MAX = 16
ID_BITS = 32
SEED = 0


def make_lexicon(dim: int = DIM, v_max: int = V_MAX, seed: int = SEED) -> Lexicon:
    """按测试默认参数建一张共享词表。"""
    return Lexicon(dim=dim, v_max=v_max, id_bits=ID_BITS, dtype=torch.float32, seed=seed)


def test_initial_shape_and_dtype() -> None:
    lexicon = make_lexicon()
    assert lexicon.dim == DIM
    assert lexicon.size == V_MAX
    assert lexicon.id_bits == ID_BITS
    assert lexicon.version == 1
    assert lexicon.frozen is False
    assert lexicon.vectors.shape == (V_MAX, DIM)
    assert lexicon.vectors.dtype == torch.float32


def test_initialization_is_reproducible() -> None:
    assert torch.equal(make_lexicon().vectors, make_lexicon().vectors)
    assert not torch.equal(make_lexicon(seed=1).vectors, make_lexicon(seed=2).vectors)


def test_vectors_are_trainable_by_default() -> None:
    assert make_lexicon().vectors.requires_grad is True


def test_vector_lookup_matches_table() -> None:
    lexicon = make_lexicon()
    assert torch.equal(lexicon.vector(3), lexicon.vectors[3])


@pytest.mark.parametrize("word_id", [-1, V_MAX])
def test_vector_lookup_out_of_range(word_id: int) -> None:
    with pytest.raises(IndexError):
        make_lexicon().vector(word_id)


def test_batch_lookup() -> None:
    lexicon = make_lexicon()
    ids = torch.tensor([0, 2, 5])
    vectors = lexicon.vectors_of(ids)
    assert vectors.shape == (3, DIM)
    assert torch.equal(vectors, lexicon.vectors[torch.tensor([0, 2, 5])])


def test_hex_round_trip() -> None:
    lexicon = make_lexicon()
    assert lexicon.hex_of(3) == "00000003"
    assert lexicon.word_id_of("00000003") == 3


def test_hex_beyond_table_is_rejected() -> None:
    with pytest.raises(IndexError):
        make_lexicon().word_id_of("000000ff")


def test_freeze_locks_the_table() -> None:
    lexicon = make_lexicon()
    lexicon.freeze()
    assert lexicon.frozen is True
    assert lexicon.vectors.requires_grad is False


@pytest.mark.parametrize(("dim", "v_max"), [(0, V_MAX), (DIM, 0)])
def test_non_positive_shape_is_rejected(dim: int, v_max: int) -> None:
    with pytest.raises(ValueError, match="必须为正"):
        make_lexicon(dim=dim, v_max=v_max)


def test_id_hex_helpers_reject_bad_bits() -> None:
    with pytest.raises(ValueError, match="4 的正整数倍"):
        id_to_hex(0, bits=7)
    with pytest.raises(ValueError, match="4 的正整数倍"):
        hex_to_id("0", bits=0)


def test_id_to_hex_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="可表示的范围"):
        id_to_hex(1 << 32, bits=32)


def test_hex_to_id_rejects_wrong_width() -> None:
    with pytest.raises(ValueError, match="hex 长度须为 8"):
        hex_to_id("ff", bits=32)


def test_builds_from_repo_config() -> None:
    config_path = Path(__file__).resolve().parents[3] / "configs" / "config.yaml"
    config = OmegaConf.load(config_path)
    language = config.language
    lexicon = Lexicon(
        dim=language.dim,
        v_max=language.v_max,
        id_bits=language.id_bits,
        dtype=getattr(torch, language.dtype),
        seed=config.seed,
    )
    assert lexicon.dim == 128
    assert lexicon.size == 1024
