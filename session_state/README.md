# 会话状态目录（v3.7.0）

本目录由 Session State Manager（stateful-drilldown）自动维护，支持同一会话多轮下钻追问、上下文累积不丢、崩溃可恢复（对齐 LangGraph checkpoint）。

文件：`session_state/<session_id>.json`（turns[] / drill_tree / cumulative_conclusion / checkpoint）。
多轮下钻时复用历史 provenance/variables，不重采不重算；单轮研究可不写入。
