# SPDX-FileCopyrightText: 2026 HanYang06
# SPDX-License-Identifier: Apache-2.0

"""词表：ID ＋ 向量载体；全局唯一、共享、外部（见设计篇 §3）。"""

from lna.models.lexicon.ids import hex_to_id, id_to_hex
from lna.models.lexicon.lexicon import Lexicon


__all__ = ["Lexicon", "hex_to_id", "id_to_hex"]
