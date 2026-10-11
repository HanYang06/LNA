# SPDX-FileCopyrightText: 2026 HanYang06
# SPDX-License-Identifier: Apache-2.0

"""词表：全体模型共享的一份「ID → 向量」参照系（设计篇 §3）。"""

import torch
from torch import nn
from torch.nn import functional

from lna.models.lexicon.ids import hex_to_id, id_to_hex


class Lexicon(nn.Module):
    """一个词 = ID + 向量；这张表就是全体模型共享的参照系。

    - **ID** 管寻址 / 版本 / 路由：离散、封闭、定宽（32 位 → 8 位 hex）。
    - **向量** 管可导性：浮点 ``nn.Parameter``，梯度能流经这张表——即术语表里的「幽灵模型」，
      有参数、挨梯度、无自己的前向，只活在别的模型引用它的时候。

    这张表**全局唯一、外部**：全体模型引用**同一个实例**（由调度核心负责装配），因此
    不存在「两份表对不上」，无需两两对齐。它是模型引用的参照系，**不是**模型自己的 embedding。
    """

    vectors: nn.Parameter

    def __init__(
        self,
        *,
        dim: int,
        v_max: int,
        id_bits: int,
        dtype: torch.dtype,
        seed: int,
    ) -> None:
        """建一张空的（随机初始化的）共享词表。

        Args:
            dim: 向量维度 D。
            v_max: 词表容量（词数上限）；起步 1024，见配置。
            id_bits: ID 位宽；32 位 → 8 位 hex。
            dtype: 向量精度；参照系要精确、可复现，起步 float32。
            seed: 随机初始化种子，保可复现。

        Raises:
            ValueError: dim 或 v_max 非正。
        """
        super().__init__()
        if dim <= 0:
            raise ValueError(f"向量维度必须为正，收到 dim={dim}")
        if v_max <= 0:
            raise ValueError(f"词表容量必须为正，收到 v_max={v_max}")
        self._id_bits = id_bits
        self._version = 1
        self._frozen = False
        # 随机初始化：无偏、词间天然可分；固定 seed 保可复现（设计篇 §3）。
        generator = torch.Generator().manual_seed(seed)
        values = torch.empty(v_max, dim, dtype=dtype)
        self.vectors = nn.Parameter(values.normal_(generator=generator))

    @property
    def dim(self) -> int:
        """向量维度 D。"""
        return self.vectors.shape[1]

    @property
    def size(self) -> int:
        """当前词数。"""
        return self.vectors.shape[0]

    @property
    def id_bits(self) -> int:
        """ID 位宽。"""
        return self._id_bits

    @property
    def version(self) -> int:
        """语言版本号——这张表本身就是版本号。"""
        return self._version

    @property
    def frozen(self) -> bool:
        """是否已固化。固化即冻结：此后不得改动已有条目。"""
        return self._frozen

    def vector(self, word_id: int) -> torch.Tensor:
        """取单个词的向量（可导）。

        Args:
            word_id: 整数 ID。

        Returns:
            形状 (dim,) 的向量。

        Raises:
            IndexError: word_id 不在本表范围内。
        """
        self._check_id(word_id)
        return self.vectors[word_id]

    def vectors_of(self, word_ids: torch.Tensor) -> torch.Tensor:
        """批量取词序列的向量（查表，可导）。

        Args:
            word_ids: 整数张量，形如 (L,)。

        Returns:
            形状 (L, dim) 的向量张量。
        """
        return functional.embedding(word_ids, self.vectors)

    def hex_of(self, word_id: int) -> str:
        """把词 ID 转成定宽 hex（寻址 / 版本 / 路由用的外部表示）。

        Args:
            word_id: 整数 ID。

        Returns:
            定宽 hex 字符串。

        Raises:
            IndexError: word_id 不在本表范围内。
        """
        self._check_id(word_id)
        return id_to_hex(word_id, bits=self._id_bits)

    def word_id_of(self, text: str) -> int:
        """把 hex 还原成词 ID，并校验其落在本表范围内。

        Args:
            text: 定宽 hex 字符串。

        Returns:
            整数 ID。

        Raises:
            IndexError: 还原出的 ID 不在本表范围内。
        """
        word_id = hex_to_id(text, bits=self._id_bits)
        self._check_id(word_id)
        return word_id

    def freeze(self) -> None:
        """固化当前表为一个语言版本：锁死已有条目，梯度不再流经本表。"""
        self.vectors.requires_grad = False
        self._frozen = True

    def _check_id(self, word_id: int) -> None:
        if not 0 <= word_id < self.size:
            raise IndexError(f"词 ID 越界：{word_id}；本表范围 [0, {self.size})")
