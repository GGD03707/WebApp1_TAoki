"""
自宅のネットワークトラブル解決教材アプリ
Streamlit + matplotlib のみで動作する単一ファイル構成。
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ============================================================
# 基本設定
# ============================================================
st.set_page_config(page_title="ネットワークトラブル解決教材", page_icon="🖧", layout="centered")

# 疎通確認先とその結果（あらかじめ決められたシナリオ：①HUB〜デスクトップPC間の断線）
CHECK_TARGETS = [
    {"key": "a", "label": "a. ルーター", "result": "〇"},
    {"key": "b", "label": "b. 無線LANアクセスポイント", "result": "〇"},
    {"key": "c", "label": "c. デスクトップPC", "result": "×"},
    {"key": "d", "label": "d. プリンタ", "result": "〇"},
]

CAUSE_OPTIONS = {
    "①": "LANケーブルの接触不良・断線（ノートPC〜無線AP間、無線AP〜HUB間、またはHUB〜デスクトップPC間）",
    "②": "HUBの障害（特定ポートの故障）",
    "③": "無線LANアクセスポイントの障害（無線AP本体の故障）",
    "④": "ルーターの障害（ルーター本体の故障、または特定ポートの不具合）",
}
CORRECT_CAUSE = "①"

# ============================================================
# セッション状態の初期化
# ============================================================
def init_state():
    defaults = {
        "started": False,
        "trouble_occurred": False,
        "checking_started": False,
        "tested": {t["key"]: False for t in CHECK_TARGETS},
        "answer_submitted": False,
        "selected_cause": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()


init_state()

# ============================================================
# ネットワーク構成図の描画
# ============================================================
def draw_network(highlight_break: bool = False, dim_unreachable: bool = False):
    # SVGA (800x600px, 4:3) の画面サイズに合わせて描画
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = {
        "ISP": (1.0, 5.2),
        "ルーター": (3.3, 5.2),
        "HUB": (3.3, 3.5),
        "無線AP": (1.6, 1.9),
        "ノートPC": (1.6, 0.5),
        "デスクトップPC": (5.6, 1.9),
        "プリンタ": (5.6, 0.5),
    }

    box_w, box_h = 1.5, 0.7

    def box_color(name):
        if dim_unreachable and name in ("デスクトップPC",):
            return "#f8d7da"
        return "#dce6f1"

    def edge_color(name):
        if dim_unreachable and name in ("デスクトップPC",):
            return "#c0392b"
        return "#4472c4"

    # 接続線を先に描画
    edges = [
        ("ISP", "ルーター", "solid", False),
        ("ルーター", "HUB", "solid", False),
        ("HUB", "無線AP", "solid", False),
        ("無線AP", "ノートPC", "dashed", False),  # 無線
        ("HUB", "デスクトップPC", "solid", True),  # 障害箇所の候補
        ("HUB", "プリンタ", "solid", False),
    ]

    for a, b, style, is_break_candidate in edges:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        color = "#999999"
        lw = 1.8
        if highlight_break and is_break_candidate:
            color = "#c0392b"
            lw = 3.0
        ax.plot([x1, x2], [y1, y2], linestyle=style, color=color, linewidth=lw, zorder=1)
        if highlight_break and is_break_candidate:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.plot(mx, my, marker="x", color="#c0392b", markersize=18, mew=4, zorder=3)

    # ノードを描画
    for name, (x, y) in nodes.items():
        fc = box_color(name)
        ec = edge_color(name)
        rect = mpatches.FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.05,rounding_size=0.08",
            linewidth=1.8, edgecolor=ec, facecolor=fc, zorder=2,
        )
        ax.add_patch(rect)
        ax.text(x, y, name, ha="center", va="center", fontsize=10, zorder=4)

    ax.text(2.45, 3.75, "(有線)", fontsize=8, color="#666666", ha="center")
    ax.text(1.85, 1.2, "(無線)", fontsize=8, color="#666666", ha="center")
    ax.text(4.6, 3.75, "(有線)", fontsize=8, color="#666666", ha="center")
    ax.text(4.9, 1.2, "(有線)", fontsize=8, color="#666666", ha="center")

    return fig


# ============================================================
# 画面構成
# ============================================================
st.title("🖧 自宅のネットワークトラブル解決教材")
st.caption("ネットワーク機器の疎通確認を行いながら、トラブルの原因を推理しよう")

with st.sidebar:
    st.header("操作")
    if st.button("🔄 最初からやり直す", use_container_width=True):
        reset_app()
        st.rerun()

    with st.expander("📘 ナレッジメモ（機器の役割）", expanded=False):
        st.markdown(
            """
**① ISP（インターネットサービスプロバイダ）**
自宅のLANとインターネットを接続する事業者。今回の対象外（正常とみなす）。

**② ルーター**
異なるネットワーク間の経路制御（レイヤー3）を行う。故障すると通信全体・DHCPに影響。

**③ HUB**
同一ネットワーク内の複数機器を中継する。ポート故障は直下の機器のみに影響。

**④ 無線LANアクセスポイント**
有線LANと無線LAN（Wi-Fi）を橋渡しする。故障すると無線端末全体が遮断される。
            """
        )

# ------------------------------------------------------------
# ステップ1: スタート
# ------------------------------------------------------------
st.subheader("ステップ1：ネットワーク構成の確認")
if not st.session_state.started:
    if st.button("▶ スタート", type="primary"):
        st.session_state.started = True
        st.rerun()
else:
    st.pyplot(draw_network(), use_container_width=False)

    # ------------------------------------------------------------
    # ステップ2: トラブル発生
    # ------------------------------------------------------------
    st.subheader("ステップ2：トラブル発生")
    if not st.session_state.trouble_occurred:
        if st.button("⚠ トラブル発生", type="primary"):
            st.session_state.trouble_occurred = True
            st.rerun()
    else:
        st.error("ノートPCからデスクトップPCへのネットワーク接続ができません")

        # ------------------------------------------------------------
        # ステップ3: 疎通確認
        # ------------------------------------------------------------
        st.subheader("ステップ3：疎通確認")
        if not st.session_state.checking_started:
            if st.button("🔍 ノートPCから疎通確認を行います"):
                st.session_state.checking_started = True
                st.rerun()
        else:
            st.info("ノートPCから疎通確認を行います")
            st.write("下のボタンをクリックして、各機器への疎通を確認してください。")

            cols = st.columns(len(CHECK_TARGETS))
            for i, target in enumerate(CHECK_TARGETS):
                with cols[i]:
                    if st.button(f"{target['label']} に確認", key=f"check_{target['key']}"):
                        st.session_state.tested[target["key"]] = True
                        st.rerun()

            # 結果テーブル（クリックしたものだけ結果を表示）
            st.markdown("**疎通確認結果**")
            table_md = "| 疎通確認先 | 疎通確認結果 |\n|---|---|\n"
            any_tested = False
            for target in CHECK_TARGETS:
                if st.session_state.tested[target["key"]]:
                    table_md += f"| {target['label']} | {target['result']} |\n"
                    any_tested = True
                else:
                    table_md += f"| {target['label']} | (未確認) |\n"
            st.markdown(table_md)

            if not any_tested:
                st.caption("まだ確認していません。上のボタンをクリックしてください。")

            # ------------------------------------------------------------
            # ステップ4: 原因の推理
            # ------------------------------------------------------------
            all_tested = all(st.session_state.tested.values())
            if all_tested:
                st.subheader("ステップ4：トラブル原因の推理")
                st.write("確認結果から、トラブルの原因として最も可能性が高いものを選んでください。")

                if not st.session_state.answer_submitted:
                    choice = st.radio(
                        "原因を選択",
                        options=list(CAUSE_OPTIONS.keys()),
                        format_func=lambda k: f"{k} {CAUSE_OPTIONS[k]}",
                    )
                    if st.button("✅ 回答する", type="primary"):
                        st.session_state.selected_cause = choice
                        st.session_state.answer_submitted = True
                        st.rerun()
                else:
                    selected = st.session_state.selected_cause
                    st.write(f"あなたの回答：**{selected} {CAUSE_OPTIONS[selected]}**")

                    if selected == CORRECT_CAUSE:
                        st.success("正解です！🎉")
                    else:
                        st.warning("残念、不正解です。")

                    st.markdown("### 解説")
                    st.markdown(
                        """
- ルーター（a）・無線LANアクセスポイント（b）・プリンタ（d）への疎通は **〇** でした。
- デスクトップPC（c）への疎通のみ **×** でした。
- ルーターと無線APが正常に動作しているということは、HUBの主要機能とルーター本体も
  正常に働いていると考えられます。
- デスクトップPCだけが孤立していることから、**HUB〜デスクトップPC間のLANケーブルの
  接触不良・断線（①）** が最も可能性の高い原因です。
- ②HUB自体の故障であれば、他のポート（無線APなど）にも影響が出る可能性がありますが、
  今回は無線AP経由の通信は正常でした。
- ③無線APの故障であれば、ノートPC自体がネットワークに接続できなくなります。
- ④ルーターの故障であれば、ルーターへの疎通確認自体が失敗するはずです。
                        """
                    )

                    st.pyplot(draw_network(highlight_break=True, dim_unreachable=True), use_container_width=False)

                    if st.button("🔄 もう一度挑戦する"):
                        reset_app()
                        st.rerun()