# SPDX-FileCopyrightText: 2026 HanYang06
# SPDX-License-Identifier: Apache-2.0

"""冒烟测试：包可导入、入口可调用。"""

from lna import main


def test_main_runs(capsys) -> None:
    """入口应能跑通并往 stdout 写一行。"""
    main()
    assert "lna" in capsys.readouterr().out
