# SPDX-FileCopyrightText: 2026 HanYang06
# SPDX-License-Identifier: Apache-2.0

"""词的 ID：寻址 / 版本 / 路由用的离散、封闭、定宽编号（设计篇 §3）。"""

__all__ = ["hex_to_id", "id_to_hex"]


def _check_bits(bits: int) -> None:
    if bits <= 0 or bits % 4 != 0:
        raise ValueError(f"ID 位宽必须是 4 的正整数倍，收到 bits={bits}")


def id_to_hex(word_id: int, *, bits: int) -> str:
    """把词的整数 ID 转成定宽 hex（32 位 → 8 位）。

    Args:
        word_id: 整数 ID。
        bits: ID 位宽，须为 4 的正整数倍。

    Returns:
        定宽小写 hex 字符串。

    Raises:
        ValueError: 位宽非法，或 word_id 超出该位宽可表示的范围。
    """
    _check_bits(bits)
    if not 0 <= word_id < (1 << bits):
        raise ValueError(f"词 ID 超出 {bits} 位可表示的范围：{word_id}")
    return format(word_id, f"0{bits // 4}x")


def hex_to_id(text: str, *, bits: int) -> int:
    """把定宽 hex 还原成整数 ID。

    Args:
        text: 定宽 hex 字符串，长度须为 ``bits // 4``。
        bits: ID 位宽，须为 4 的正整数倍。

    Returns:
        整数 ID。

    Raises:
        ValueError: 位宽非法、长度不符，或 text 不是合法 hex。
    """
    _check_bits(bits)
    if len(text) != bits // 4:
        raise ValueError(f"hex 长度须为 {bits // 4}，收到 {len(text)}：{text!r}")
    return int(text, 16)
