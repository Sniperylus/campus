import streamlit as st
import pandas as pd
import hashlib
import os
from PIL import Image, ImageOps
import base64
from io import BytesIO
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Campus AI Agent Lost & Found", layout="wide")

# ===================== 主题配色配置 =====================
THEMES = {
    "white": {"bg": "#ffffff", "text": "#17211d", "sidebar": "#f0f4f1", "primary": "#176b55", "primary_hover": "#105541", "border": "#e5ece7", "card": "#ffffff", "header": "rgba(255,255,255,.78)"},
    "black": {"bg": "#121212", "text": "#e8e8e8", "sidebar": "#1e1e1e", "primary": "#bb86fc", "primary_hover": "#9d63d8", "border": "#333333", "card": "#1e1e1e", "header": "rgba(30,30,30,.85)"},
    "gray":  {"bg": "#f5f5f5", "text": "#2b2b2b", "sidebar": "#e8e8e8", "primary": "#4a4a4a", "primary_hover": "#2d2d2d", "border": "#d0d0d0", "card": "#ffffff", "header": "rgba(255,255,255,.85)"},
    "pink":  {"bg": "#fff7f9", "text": "#3a2a30", "sidebar": "#fde8ef", "primary": "#e85d8b", "primary_hover": "#d13d6f", "border": "#f5d6e0", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
    "green": {"bg": "#f4f8f4", "text": "#1e2b1e", "sidebar": "#e3efe3", "primary": "#2e7d32", "primary_hover": "#1b5e20", "border": "#c8e0c8", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
    "blue":  {"bg": "#f3f7fb", "text": "#1a2540", "sidebar": "#dbe6f5", "primary": "#1976d2", "primary_hover": "#0d47a1", "border": "#c5d5ed", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
    "red":   {"bg": "#fff7f7", "text": "#3a1a1a", "sidebar": "#fbe0e0", "primary": "#d32f2f", "primary_hover": "#b71c1c", "border": "#f5c8c8", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
    "yellow":{"bg": "#fffbf0", "text": "#3a2e12", "sidebar": "#fbeec2", "primary": "#f9a825", "primary_hover": "#f57f17", "border": "#f3dca0", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
    "purple":{"bg": "#f9f5fc", "text": "#2a1a3a", "sidebar": "#eadff5", "primary": "#7b1fa2", "primary_hover": "#4a148c", "border": "#d6c4e8", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
    "orange":{"bg": "#fff8f2", "text": "#3a2212", "sidebar": "#fde0c2", "primary": "#ef6c00", "primary_hover": "#e65100", "border": "#f5c99a", "card": "#ffffff", "header": "rgba(255,255,255,.88)"},
}

if "theme" not in st.session_state:
    st.session_state.theme = "white"
theme = THEMES[st.session_state.theme]

# CSS 样式注入 (包含 Agent 定制样式)
st.markdown(f"""
<style>
    * {{ font-family: "Segoe UI","Microsoft YaHei",sans-serif; }}
    .stApp {{ background:{theme['bg']}; color:{theme['text']}; }}
    h1,h2,h3 {{ color:{theme['text']}; font-weight:700; letter-spacing:-0.025em; }}
    [data-testid="stHeader"] {{ background:{theme['header']}; }}
    [data-testid="stSidebar"] {{ background:{theme['sidebar']}; border-right:1px solid {theme['border']}; }}
    [data-testid="stMain"] > div {{ padding-top:2rem; }}
    
    .stButton>button {{ background:{theme['primary']}; color:#fff; border:1px solid {theme['primary']}; border-radius:12px; min-height:2.65rem; font-weight:600; transition:all .18s ease; }}
    .stButton>button:hover {{ background:{theme['primary_hover']}; border-color:{theme['primary_hover']}; color:#fff; transform:translateY(-1px); }}
    
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: {theme['card']} !important; 
        color: {theme['text']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 10px;
    }}
    ul[data-testid="stSelectboxVirtualDropdown"] {{ background-color: {theme['card']} !important; }}
    ul[data-testid="stSelectboxVirtualDropdown"] li {{ color: {theme['text']} !important; }}
    
    hr {{ border-color:{theme['border']}; margin:1.5rem 0; }}
    .card {{ background:{theme['card']}; border:1px solid {theme['border']}; padding:1.25rem; border-radius:16px; margin-bottom:1rem; box-shadow:0 8px 28px rgba(0,0,0,.04); }}
    .hero-card {{ background:linear-gradient(120deg,{theme['primary_hover']},{theme['primary']} 60%); color:#fff; padding:2.4rem; border-radius:24px; margin:.4rem 0 1.5rem; box-shadow:0 16px 40px rgba(0,0,0,.12); }}
    .hero-card h1 {{ color:#fff; font-size:2.4rem; margin:.4rem 0; }}
    .hero-card p {{ color:rgba(255,255,255,.9); font-size:1.05rem; max-width:46rem; }}
    .hero-kicker {{ color:rgba(255,255,255,.82); text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; font-weight:700; }}
    .feature-card {{ background:rgba(255,255,255,.88); border:1px solid {theme['border']}; padding:1.4rem; border-radius:18px; min-height:9.5rem; box-shadow:0 8px 24px rgba(0,0,0,.03); }}
    [data-testid="stMetric"] {{ background:rgba(255,255,255,.85); padding:1rem 1.2rem; border:1px solid {theme['border']}; border-radius:16px; }}
    
    /* Agent 专属卡片 */
    .agent-card {{ background:{theme['card']}; border:2px dashed {theme['primary']}; padding:1rem; border-radius:12px; margin-bottom:1rem; text-align:center; }}
    .agent-avatar-emoji {{ font-size:3rem; line-height: 1.2; }}
    .agent-avatar-img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin: 0 auto 10px auto; display: block; border: 2px solid {theme['primary']}; }}
</style>
""", unsafe_allow_html=True)

os.makedirs("media", exist_ok=True)

DATA_FILES = {
    "users": "users.csv", "lost_items": "lost_items.csv", "posts": "forum_posts.csv",
    "messages": "messages.csv", "likes": "post_likes.csv", "collects": "post_collects.csv",
}

def _ensure_csv(path, columns):
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)
        return
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        for c in columns:
            if c not in df.columns:
                df[c] = "0" if c in ("likes", "collects") else ""
        df[columns].to_csv(path, index=False)
    except Exception:
        pd.DataFrame(columns=columns).to_csv(path, index=False)

def init_csv():
    _ensure_csv(DATA_FILES["users"], ["username", "password", "name", "age", "signature", "avatar"])
    _ensure_csv(DATA_FILES["lost_items"], ["id", "type", "item_name", "category", "color", "location", "time", "desc", "contact", "owner", "status"])
    _ensure_csv(DATA_FILES["posts"], ["id", "title", "content", "media", "author", "time", "comments", "type", "ref_id", "likes", "collects"])
    _ensure_csv(DATA_FILES["messages"], ["id", "sender", "receiver", "content", "time"])
    _ensure_csv(DATA_FILES["likes"], ["username", "post_id"])
    _ensure_csv(DATA_FILES["collects"], ["username", "post_id"])

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def get_user_avatar(username):
    if not username or not os.path.exists(DATA_FILES["users"]):
        return None
    try:
        users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
        m = users.loc[users["username"] == str(username), "avatar"]
        if m.empty or not m.iloc[0]:
            return None
        v = m.iloc[0].strip()
        if v.startswith("data:") and "," in v:
            v = v.split(",", 1)[1]
        return Image.open(BytesIO(base64.b64decode(v))).copy()
    except Exception:
        return None

def encode_avatar(uploaded_file):
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img)
    # 裁剪为正方形以适配圆形头像
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim)/2
    top = (height - min_dim)/2
    right = (width + min_dim)/2
    bottom = (height + min_dim)/2
    img = img.crop((left, top, right, bottom))
    
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def save_media_file(uploaded_file, post_id):
    if uploaded_file is None:
        return ""
    fname = f"post_{post_id}_{uploaded_file.name}"
    with open(os.path.join("media", fname), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return fname

# ===================== 点赞 / 收藏 =====================
def _read_rel(path):
    if not os.path.exists(path):
        return pd.DataFrame(columns=["username", "post_id"])
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        for c in ("username", "post_id"):
            if c not in df.columns: df[c] = ""
        return df[["username", "post_id"]].astype(str)
    except Exception:
        return pd.DataFrame(columns=["username", "post_id"])

def _read_posts():
    posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("")
    for c in ("likes", "collects"):
        if c not in posts.columns: posts[c] = "0"
        posts[c] = pd.to_numeric(posts[c], errors="coerce").fillna(0).astype(int)
    posts["id"] = posts["id"].astype(str)
    return posts

def is_liked(username, post_id):
    if not st.session_state.get("logged_in", False): return False
    df = _read_rel(DATA_FILES["likes"])
    return not df[(df["username"] == str(username)) & (df["post_id"] == str(post_id))].empty

def is_collected(username, post_id):
    if not st.session_state.get("logged_in", False): return False
    df = _read_rel(DATA_FILES["collects"])
    return not df[(df["username"] == str(username)) & (df["post_id"] == str(post_id))].empty

def _toggle_rel(path, col, username, post_id):
    username, post_id = str(username), str(post_id)
    rel = _read_rel(path)
    posts = _read_posts()
    if post_id not in posts["id"].values: return
    mr = (rel["username"] == username) & (rel["post_id"] == post_id)
    mp = posts["id"] == post_id
    cur = int(posts.loc[mp, col].iloc[0])
    if mr.any():
        rel = rel[~mr]
        posts.loc[mp, col] = max(0, cur - 1)
    else:
        rel = pd.concat([rel, pd.DataFrame([{"username": username, "post_id": post_id}])], ignore_index=True)
        posts.loc[mp, col] = cur + 1
    rel.to_csv(path, index=False)
    posts.to_csv(DATA_FILES["posts"], index=False)

def toggle_like(u, p): _toggle_rel(DATA_FILES["likes"], "likes", u, p)
def toggle_collect(u, p): _toggle_rel(DATA_FILES["collects"], "collects", u, p)

# ===================== 多语言文本 (已完整翻译) =====================
LANG = {
    "中文": {
        "nav_home": "首页", "nav_lost": "失物招领", "nav_forum": "校园论坛", "nav_profile": "个人中心", "nav_msg": "站内消息",
        "nav_login": "登录", "nav_logout": "退出登录", "nav_browse": "浏览失物信息", "nav_members": "校园成员",
        "theme_label": "主题配色", "theme_white": "纯白极简", "theme_black": "纯黑模式", "theme_gray": "高级灰",
        "theme_pink": "樱花粉", "theme_green": "森系绿", "theme_blue": "深海蓝", "theme_red": "热烈红",
        "theme_yellow": "暖阳黄", "theme_purple": "梦幻紫", "theme_orange": "活力橙",
        "login_title": "登录账号", "reg_title": "注册账号", "find_pwd": "忘记密码",
        "username": "用户名", "password": "密码", "pwd_confirm": "确认密码",
        "login_btn": "登录", "reg_btn": "注册", "back_login": "返回登录", "remember": "记住密码", "reset_pwd": "重置密码",
        "pwd_length_hint": "密码至少需要 6 位",
        "lost_tab1": "我丢了东西", "lost_tab2": "我捡到了东西", "upload_photo": "上传物品照片", "ai_recognize": "AI 识别物品",
        "cat_label": "物品类别", "item_name": "物品名称", "color_label": "颜色", "loc_label": "地点", "time_label": "时间",
        "desc_label": "补充描述", "contact_label": "联系方式（可选）", "submit_btn": "提交发布",
        "match_result": "匹配结果", "post_generated": "AI 生成招领文案", "submit_success": "✅ 发布成功，已同步至论坛",
        "browse_title": "浏览失物信息", "browse_desc": "查看校园里已发布的丢失与拾获信息；登录后可发布新信息。",
        "filter_type": "信息类型", "filter_all": "全部", "filter_lost": "丢失", "filter_found": "拾获",
        "filter_category": "物品类别", "search_placeholder": "输入物品、地点、描述或发布者",
        "result_count": "找到 {} 条信息", "no_result": "没有找到符合条件的信息，试试换一个关键词或筛选条件。", "no_data": "目前还没有失物信息。",
        "item_name_label": "物品名称", "color_label_full": "颜色", "desc_label_full": "描述", "contact_label_full": "联系方式",
        "owner_label": "发布者", "status_label": "状态",
        "members_title": "校园成员", "members_count": "共 {} 位成员", "member_search": "搜索成员",
        "member_search_ph": "输入用户名或姓名", "no_members": "目前还没有注册成员。", "no_member_result": "没有找到符合条件的成员。",
        "hero_kicker": "Campus AI Agent", "hero_title": "让校园互助进入 AI 时代",
        "hero_desc": "发布失物线索、分享招领信息。你的专属 AI 智能体将在后台自动为您匹配并发送通知。",
        "feature_lost": "🔎 失物招领", "feature_lost_desc": "发布丢失或捡到的物品，AI 自动拦截匹配。",
        "feature_forum": "💬 校园论坛", "feature_forum_desc": "浏览校园帖子、查看留言，也可以发布线索和互助信息。",
        "campus_stats": "校园动态", "stat_posts": "论坛帖子", "stat_items": "失物信息", "stat_members": "校园成员",
        "open_posts": "打开帖子", "find_items": "查找物品", "view_members": "查看成员",
        "forum_title": "校园失物交流论坛", "forum_desc": "共 {} 条帖子 · 最新发布显示在前", "new_post": "发布新帖",
        "post_title": "标题", "post_content": "内容", "post_btn": "发布", "comment_btn": "留言", "comment_placeholder": "写下你的留言...",
        "media_upload": "上传图片/视频/音频", "media_upload_help": "支持 JPG/PNG/MP4/MP3/WAV，可选",
        "edit_post": "编辑", "delete_post": "删除", "save_edit": "保存修改", "cancel_edit": "取消", "delete_confirm": "确定删除这条帖子吗？",
        "like": "点赞", "collect": "收藏", "liked": "已点赞", "collected": "已收藏",
        "guest_tip": "你可以先浏览校园帖子；登录后即可发帖、留言、点赞和收藏。",
        "guest_interact_tip": "登录后可点赞和收藏", "guest_comment_tip": "登录后即可参与留言。",
        "empty_forum": "论坛还没有帖子，登录后发布第一条校园动态吧。",
        "profile_title": "个人资料", "my_posts": "我的发布", "my_likes": "我的点赞", "my_collects": "我的收藏",
        "name": "姓名", "age": "年龄", "signature": "个性签名", "avatar": "头像", "save_btn": "保存修改",
        "avatar_tip": "支持 JPG、PNG、WebP、GIF 和 BMP 图片。",
        "empty_posts": "暂无发布内容", "empty_likes": "暂无点赞内容", "empty_collects": "暂无收藏内容",
        "msg_title": "站内私信", "send_to": "发送给", "msg_content": "消息内容", "send_btn": "发送",
        "inbox": "收件箱", "sent": "已发送", "chat_member": "聊天成员", "chat_history": "与 **{}** 的聊天记录",
        "no_chat": "你和 {} 还没有聊天记录，发送第一条消息吧。", "msg_placeholder": "写点什么……",
        "no_members_tip": "暂时没有其他成员。邀请成员注册后即可开始聊天。",
        "empty_inbox": "暂无收到的消息", "empty_sent": "暂无已发送消息",
        "time_opts": ["上午", "中午", "下午", "晚上"],
        "categories": ["电子产品", "证件卡类", "学习用品", "生活用品", "衣物配饰", "书籍文件"],
        "data_note": "数据来源：校园地图 + 公开失物信息", "not_login": "请先登录后使用完整功能",
        "no_permission": "无权限操作", "deleted": "已删除",
        "api_provider": "AI 平台", "api_key": "API 密钥", "api_demo": "不填则使用演示模式",
        "type_lost": "失物求助", "type_found": "拾物招领", "type_normal": "普通帖子",
        "lang_label": "语言 / Language", "search_btn": "搜索", "from": "来自", "to": "发给",
        # Agent 专属翻译
        "agent_settings": "🧠 你的专属 AI 智能体", "agent_name": "智能体命名", "agent_avatar_emoji": "选择表情头像",
        "agent_avatar_upload": "上传自定义头像", "agent_clear_avatar": "清除自定义头像", "agent_voice": "语音播报音色",
        "agent_voice_machine": "🤖 机械/沉稳音", "agent_voice_girl": "👧 甜美/高音", "agent_voice_boy": "👦 标准男声",
        "agent_greeting_lost": "别着急，请填写详细信息，我会在后台全力为您寻找匹配项！",
        "agent_greeting_found": "感谢你的拾金不昧，我来帮你通知失主！",
        "agent_notify_msg": "【{} 智能通知】\n系统发现高度匹配的信息！\n您的【{}】可能与 {} 发布的信息匹配（匹配度 {}%）。请及时通过站内信联系！",
        "agent_speak_msg": "主人，我是{}，我已经为您找到了匹配的物品，并发送了通知。",
        "agent_matched": "🎯 **{}** 已为您拦截到匹配信息，并自动私信通知了 {}！",
        "agent_monitoring": "🤖 {} 正在后台为您持续监控匹配信息...",
        "agent_intervened": "🤖 AI 智能体已介入",
    },
    "한국어": {
        "nav_home": "홈", "nav_lost": "분실물", "nav_forum": "게시판", "nav_profile": "내 정보", "nav_msg": "쪽지",
        "nav_login": "로그인", "nav_logout": "로그아웃", "nav_browse": "분실물 둘러보기", "nav_members": "캠퍼스 멤버",
        "theme_label": "테마 색상", "theme_white": "화이트 모드", "theme_black": "다크 모드", "theme_gray": "그레이 모드",
        "theme_pink": "핑크", "theme_green": "그린", "theme_blue": "블루", "theme_red": "레드",
        "theme_yellow": "옐로우", "theme_purple": "퍼플", "theme_orange": "오렌지",
        "login_title": "로그인", "reg_title": "회원가입", "find_pwd": "비밀번호 찾기",
        "username": "아이디", "password": "비밀번호", "pwd_confirm": "비밀번호 확인",
        "login_btn": "로그인", "reg_btn": "가입하기", "back_login": "로그인으로 돌아가기",
        "remember": "비밀번호 기억하기", "reset_pwd": "비밀번호 재설정",
        "pwd_length_hint": "비밀번호는 최소 6자 이상이어야 합니다",
        "lost_tab1": "물건을 잃어버렸어요", "lost_tab2": "물건을 주웠어요", "upload_photo": "물건 사진 업로드",
        "ai_recognize": "AI 물건 인식", "cat_label": "물품 종류", "item_name": "물품명", "color_label": "색상",
        "loc_label": "장소", "time_label": "시간", "desc_label": "추가 설명", "contact_label": "연락처 (선택)",
        "submit_btn": "등록하기", "match_result": "매칭 결과", "post_generated": "AI 게시글 생성",
        "submit_success": "✅ 등록 완료, 게시판에 자동 공개됨",
        "browse_title": "분실물 둘러보기", "browse_desc": "캠퍼스에 등록된 분실물/습득물 정보를 확인하세요. 로그인 후 새로 등록할 수 있습니다.",
        "filter_type": "정보 종류", "filter_all": "전체", "filter_lost": "분실", "filter_found": "습득",
        "filter_category": "물품 종류", "search_placeholder": "물건, 장소, 설명, 작성자 검색",
        "result_count": "{}건의 정보를 찾았습니다", "no_result": "조건에 맞는 정보가 없습니다. 다른 키워드로 검색해보세요.",
        "no_data": "아직 등록된 분실물 정보가 없습니다.",
        "item_name_label": "물품명", "color_label_full": "색상", "desc_label_full": "설명", "contact_label_full": "연락처",
        "owner_label": "작성자", "status_label": "상태",
        "members_title": "캠퍼스 멤버", "members_count": "총 {}명의 멤버", "member_search": "멤버 검색",
        "member_search_ph": "아이디 또는 이름으로 검색", "no_members": "아직 가입한 멤버가 없습니다.",
        "no_member_result": "조건에 맞는 멤버가 없습니다.",
        "hero_kicker": "Campus AI Agent", "hero_title": "캠퍼스 내 나눔을 AI 시대로",
        "hero_desc": "분실물 단서를 올리고 습득물 정보를 공유해요. 전담 AI 에이전트가 백그라운드에서 자동으로 매칭하고 알림을 보냅니다.",
        "feature_lost": "🔎 분실물", "feature_lost_desc": "잃어버린 물건이나 주운 물건을 등록하면 AI가 자동으로 매칭합니다.",
        "feature_forum": "💬 캠퍼스 게시판", "feature_forum_desc": "게시글을 둘러보고 댓글을 남기거나 단서와 도움 정보를 올릴 수 있어요.",
        "campus_stats": "캠퍼스 현황", "stat_posts": "게시글", "stat_items": "분실물 정보", "stat_members": "캠퍼스 멤버",
        "open_posts": "게시판 열기", "find_items": "물건 찾기", "view_members": "멤버 보기",
        "forum_title": "캠퍼스 분실물 게시판", "forum_desc": "총 {}개의 게시글 · 최신순으로 표시됩니다", "new_post": "글 쓰기",
        "post_title": "제목", "post_content": "내용", "post_btn": "게시", "comment_btn": "댓글", "comment_placeholder": "댓글을 남겨주세요...",
        "media_upload": "사진/영상/음악 업로드", "media_upload_help": "JPG/PNG/MP4/MP3/WAV 지원, 선택사항",
        "edit_post": "수정", "delete_post": "삭제", "save_edit": "저장", "cancel_edit": "취소", "delete_confirm": "정말 삭제하시겠습니까?",
        "like": "좋아요", "collect": "저장", "liked": "좋아요 함", "collected": "저장됨",
        "guest_tip": "게시글을 먼저 둘러보세요. 로그인하면 글쓰기, 댓글, 좋아요, 저장이 가능합니다.",
        "guest_interact_tip": "로그인 후 좋아요와 저장을 할 수 있습니다", "guest_comment_tip": "로그인 후 댓글을 남길 수 있습니다.",
        "empty_forum": "아직 게시글이 없습니다. 로그인 후 첫 글을 올려보세요.",
        "profile_title": "내 정보", "my_posts": "내가 쓴 글", "my_likes": "좋아요 한 글", "my_collects": "저장한 글",
        "name": "이름", "age": "나이", "signature": "자기소개", "avatar": "프로필 사진", "save_btn": "저장",
        "avatar_tip": "JPG, PNG, WebP, GIF, BMP 이미지를 지원합니다.",
        "empty_posts": "작성한 글이 없습니다", "empty_likes": "좋아요 한 글이 없습니다", "empty_collects": "저장한 글이 없습니다",
        "msg_title": "쪽지", "send_to": "받는 사람", "msg_content": "내용", "send_btn": "보내기",
        "inbox": "받은 쪽지", "sent": "보낸 쪽지", "chat_member": "채팅 상대", "chat_history": "**{}** 와의 대화 기록",
        "no_chat": "{} 와의 대화 기록이 없습니다. 첫 메시지를 보내보세요.", "msg_placeholder": "메시지를 입력하세요……",
        "no_members_tip": "아직 다른 멤버가 없습니다. 멤버를 초대하면 채팅을 시작할 수 있습니다.",
        "empty_inbox": "받은 쪽지가 없습니다", "empty_sent": "보낸 쪽지가 없습니다",
        "time_opts": ["오전", "점심", "오후", "저녁"],
        "categories": ["전자기기", "신분증/카드", "학용품", "생활용품", "의류/악세사리", "도서/서류"],
        "data_note": "데이터: 캠퍼스 지도 + 공개 분실물 정보", "not_login": "로그인 후 모든 기능을 이용하실 수 있습니다",
        "no_permission": "권한이 없습니다", "deleted": "삭제됨",
        "api_provider": "AI 플랫폼", "api_key": "API 키", "api_demo": "입력하지 않으면 데모 모드로 실행",
        "type_lost": "분실물 찾기", "type_found": "습득물 안내", "type_normal": "일반 글",
        "lang_label": "언어 / Language", "search_btn": "검색", "from": "보낸 사람", "to": "받는 사람",
        # Agent 专属翻译
        "agent_settings": "🧠 나만의 AI 에이전트", "agent_name": "에이전트 이름", "agent_avatar_emoji": "이모지 아바타 선택",
        "agent_avatar_upload": "커스텀 아바타 업로드", "agent_clear_avatar": "커스텀 아바타 삭제", "agent_voice": "음성 방송 톤",
        "agent_voice_machine": "🤖 기계/차분한 목소리", "agent_voice_girl": "👧 달콤/높은 목소리", "agent_voice_boy": "👦 표준 남성 목소리",
        "agent_greeting_lost": "걱정 마세요. 상세 정보를 입력하시면 제가 백그라운드에서 매칭을 찾아드릴게요!",
        "agent_greeting_found": "주인을 찾아주셔서 감사합니다. 제가 주인에게 알려드릴게요!",
        "agent_notify_msg": "【{} 스마트 알림】\n시스템에서 일치하는 정보를 발견했습니다!\n귀하의 【{}】이(가) {} 님이 게시한 정보와 일치할 수 있습니다(일치율 {}%). 쪽지로 연락해 주세요!",
        "agent_speak_msg": "주인님, 저는 {}입니다. 일치하는 물건을 찾아 알림을 보냈습니다.",
        "agent_matched": "🎯 **{}** 님이 매칭 정보를 포착하여 {} 님에게 자동으로 쪽지를 보냈습니다!",
        "agent_monitoring": "🤖 {} 님이 백그라운드에서 지속적으로 모니터링 중입니다...",
        "agent_intervened": "🤖 AI 에이전트 개입됨",
    },
    "English": {
        "nav_home": "Home", "nav_lost": "Lost & Found", "nav_forum": "Forum", "nav_profile": "Profile", "nav_msg": "Messages",
        "nav_login": "Login", "nav_logout": "Logout", "nav_browse": "Browse Items", "nav_members": "Campus Members",
        "theme_label": "Theme Color", "theme_white": "Light White", "theme_black": "Dark Mode", "theme_gray": "Elegant Gray",
        "theme_pink": "Sakura Pink", "theme_green": "Forest Green", "theme_blue": "Deep Blue", "theme_red": "Vivid Red",
        "theme_yellow": "Warm Yellow", "theme_purple": "Dreamy Purple", "theme_orange": "Vibrant Orange",
        "login_title": "Login", "reg_title": "Sign Up", "find_pwd": "Forgot Password",
        "username": "Username", "password": "Password", "pwd_confirm": "Confirm Password",
        "login_btn": "Login", "reg_btn": "Sign Up", "back_login": "Back to Login", "remember": "Remember me", "reset_pwd": "Reset Password",
        "pwd_length_hint": "Password must be at least 6 characters",
        "lost_tab1": "I Lost Something", "lost_tab2": "I Found Something", "upload_photo": "Upload Photo",
        "ai_recognize": "AI Recognize", "cat_label": "Category", "item_name": "Item Name", "color_label": "Color",
        "loc_label": "Location", "time_label": "Time", "desc_label": "Description", "contact_label": "Contact (optional)",
        "submit_btn": "Submit", "match_result": "Match Results", "post_generated": "AI Generated Post",
        "submit_success": "✅ Submitted, posted to forum automatically",
        "browse_title": "Browse Lost & Found", "browse_desc": "View all lost and found items on campus. Sign in to post new entries.",
        "filter_type": "Item Type", "filter_all": "All", "filter_lost": "Lost", "filter_found": "Found",
        "filter_category": "Category", "search_placeholder": "Search item, location, description or author",
        "result_count": "{} results found", "no_result": "No matching results. Try a different keyword or filter.",
        "no_data": "No lost & found entries yet.",
        "item_name_label": "Item Name", "color_label_full": "Color", "desc_label_full": "Description", "contact_label_full": "Contact",
        "owner_label": "Posted by", "status_label": "Status",
        "members_title": "Campus Members", "members_count": "{} members total", "member_search": "Search members",
        "member_search_ph": "Search by username or name", "no_members": "No registered members yet.",
        "no_member_result": "No members match your search.",
        "hero_kicker": "Campus AI Agent", "hero_title": "Enter the AI Era of Campus Mutual Aid",
        "hero_desc": "Post lost item clues, share found item info. Your dedicated AI agent will automatically match and send notifications in the background.",
        "feature_lost": "🔎 Lost & Found", "feature_lost_desc": "Post items you lost or found, AI auto-matches.",
        "feature_forum": "💬 Campus Forum", "feature_forum_desc": "Browse posts, leave comments, and share clues and help information.",
        "campus_stats": "Campus Stats", "stat_posts": "Forum Posts", "stat_items": "Lost Items", "stat_members": "Members",
        "open_posts": "Open Forum", "find_items": "Find Items", "view_members": "View Members",
        "forum_title": "Campus Lost & Found Forum", "forum_desc": "{} posts total · sorted by latest", "new_post": "New Post",
        "post_title": "Title", "post_content": "Content", "post_btn": "Post", "comment_btn": "Comment", "comment_placeholder": "Write a comment...",
        "media_upload": "Upload Image / Video / Audio", "media_upload_help": "Supports JPG/PNG/MP4/MP3/WAV, optional",
        "edit_post": "Edit", "delete_post": "Delete", "save_edit": "Save", "cancel_edit": "Cancel", "delete_confirm": "Are you sure to delete this post?",
        "like": "Like", "collect": "Save", "liked": "Liked", "collected": "Saved",
        "guest_tip": "Feel free to browse posts. Sign in to post, comment, like and save.",
        "guest_interact_tip": "Sign in to like and save", "guest_comment_tip": "Sign in to leave a comment.",
        "empty_forum": "No posts yet. Sign in to share the first campus update.",
        "profile_title": "My Profile", "my_posts": "My Posts", "my_likes": "My Likes", "my_collects": "Saved Posts",
        "name": "Name", "age": "Age", "signature": "Bio", "avatar": "Avatar", "save_btn": "Save Changes",
        "avatar_tip": "Supports JPG, PNG, WebP, GIF and BMP images.",
        "empty_posts": "No posts yet", "empty_likes": "No liked posts", "empty_collects": "No saved posts",
        "msg_title": "Direct Messages", "send_to": "Send to", "msg_content": "Message", "send_btn": "Send",
        "inbox": "Inbox", "sent": "Sent", "chat_member": "Chat with", "chat_history": "Conversation with **{}**",
        "no_chat": "No conversation with {} yet. Send the first message.", "msg_placeholder": "Type a message……",
        "no_members_tip": "No other members yet. Invite members to start chatting.",
        "empty_inbox": "No messages received", "empty_sent": "No messages sent",
        "time_opts": ["Morning", "Noon", "Afternoon", "Evening"],
        "categories": ["Electronics", "ID/Cards", "Supplies", "Daily Items", "Clothing", "Books/Docs"],
        "data_note": "Data: Campus map + public lost & found records", "not_login": "Please login to use all features",
        "no_permission": "No permission", "deleted": "Deleted",
        "api_provider": "AI Provider", "api_key": "API Key", "api_demo": "Leave blank for demo mode",
        "type_lost": "Lost Item", "type_found": "Found Item", "type_normal": "General Post",
        "lang_label": "Language / 언어", "search_btn": "Search", "from": "From", "to": "To",
        # Agent 专属翻译
        "agent_settings": "🧠 Your AI Agent", "agent_name": "Agent Name", "agent_avatar_emoji": "Select Emoji Avatar",
        "agent_avatar_upload": "Upload Custom Avatar", "agent_clear_avatar": "Clear Custom Avatar", "agent_voice": "Voice Tone",
        "agent_voice_machine": "🤖 Machine / Calm", "agent_voice_girl": "👧 Sweet / High", "agent_voice_boy": "👦 Standard Male",
        "agent_greeting_lost": "Don't worry, fill in the details and I'll search the background for matches!",
        "agent_greeting_found": "Thanks for your honesty, let me notify the owner for you!",
        "agent_notify_msg": "【{} Smart Alert】\nHighly matched information found!\nYour 【{}】 might match the info posted by {} (Match: {}%). Please contact via direct message!",
        "agent_speak_msg": "Master, I am {}, I have found a matching item and sent a notification.",
        "agent_matched": "🎯 **{}** intercepted a match and automatically sent a DM to {}!",
        "agent_monitoring": "🤖 {} is monitoring matches in the background...",
        "agent_intervened": "🤖 AI Agent Intervened",
    }
}

THEME_KEYS = list(THEMES.keys())
THEME_NAMES = {l: {k: LANG[l][f"theme_{k}"] for k in THEME_KEYS} for l in LANG}

LOCATIONS = {
    "中文": ["正门", "大学本部", "电算信息院", "教学楼", "图书馆", "造型艺术馆", "东门练习室", "钟门", "户外音乐堂", "第二学生会馆", "体育馆", "生活体育馆", "学生会馆", "信息印刷室", "第一工学馆", "第二工学馆", "第三工学馆", "第四工学馆", "第五工学馆", "安匠馆", "创意保育中心", "人文社会科学馆", "共同实验实习馆", "海松宿舍", "斗塔宿舍", "绿色能源研究馆", "北合体育中心", "体育场"],
    "한국어": ["정문", "대학본부", "전산정보원", "강의동", "도서관", "조형관", "동문연습실", "종문", "야외음악당", "제2학생회관", "체육관", "생활체육관", "학생회관", "정보인쇄실", "제1공학관", "제2공학관", "제3공학관", "제4공학관", "제5공학관", "안장관", "창의보육센터", "인문사회과학관", "공동실험실습관", "해송관", "두타관", "그린에너지 연구관", "북합 스포츠센터", "운동장"],
    "English": ["Main Gate", "HQ", "Computer Center", "Lecture Hall", "Library", "Art Hall", "East Practice Room", "Bell Gate", "Outdoor Auditorium", "2nd Student Union", "Gym", "Recreation Hall", "Student Union", "Printing Room", "Eng Hall 1", "Eng Hall 2", "Eng Hall 3", "Eng Hall 4", "Eng Hall 5", "Anjang Hall", "Childcare Center", "Humanities Hall", "Lab Hall", "Haesong Dorm", "Duta Dorm", "Green Energy Hall", "Bukhap Sports Center", "Stadium"],
}

API_CONFIG = {
    "Groq": {"base_url": "https://api.groq.com/openai/v1", "text_model": "llama-3.2-3b-preview", "vision_model": "llama-3.2-11b-vision-preview"},
    "OpenAI": {"base_url": "https://api.openai.com/v1", "text_model": "gpt-4o-mini", "vision_model": "gpt-4o-mini"},
}

init_csv()

for k, v in {"page": "home", "logged_in": False, "username": "", "lang": "中文",
             "api_provider": "Groq", "api_key": "", "editing_post": None,
             "confirm_delete_post": None, "ai_result": None, "submit_result": None,
             "agent_name": "Agent", "agent_avatar_emoji": "🤖", "agent_avatar_img": None, 
             "agent_voice_key": "agent_voice_machine"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

t = LANG[st.session_state.lang]

# ===================== AI 智能体核心功能 =====================
def speak_text(text, voice_key):
    if not text: return
    pitch, rate = 1.0, 1.0
    lang_code = "zh-CN"
    if st.session_state.lang == "한국어": lang_code = "ko-KR"
    elif st.session_state.lang == "English": lang_code = "en-US"

    if voice_key == "agent_voice_machine": pitch, rate = 0.6, 0.9
    elif voice_key == "agent_voice_girl": pitch, rate = 1.4, 1.1
    elif voice_key == "agent_voice_boy": pitch, rate = 0.9, 1.0
    
    safe_text = text.replace('"', '\\"').replace('\n', ' ')
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{safe_text}");
        msg.lang = '{lang_code}';
        msg.pitch = {pitch};
        msg.rate = {rate};
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0, width=0)

def ai_smart_match_and_notify(new_info, new_type, current_user):
    items = pd.read_csv(DATA_FILES["lost_items"], dtype=str).fillna("")
    candidates = items[items["type"] == ("found" if new_type == "lost" else "lost")]
    
    best_match, highest_score = None, 0
    for _, row in candidates.iterrows():
        score = 0
        if row["category"] == new_info["category"]: score += 40
        if row["color"] == new_info["color"]: score += 30
        if row["location"] == new_info["location"]: score += 30
        if score > highest_score: highest_score, best_match = score, row
            
    if highest_score >= 70 and best_match is not None:
        receiver = best_match["owner"]
        if receiver != current_user:
            msgs = pd.read_csv(DATA_FILES["messages"], dtype=str).fillna("")
            ids = pd.to_numeric(msgs.get("id", pd.Series(dtype=float)), errors="coerce")
            next_id = str(int(ids.max()) + 1) if not ids.empty and ids.notna().any() else "1"
            
            auto_msg = t["agent_notify_msg"].format(st.session_state.agent_name, best_match['item_name'], current_user, highest_score)
            pd.concat([msgs, pd.DataFrame([{"id": next_id, "sender": st.session_state.agent_name, "receiver": receiver, "content": auto_msg, "time": str(pd.Timestamp.now())}])], ignore_index=True).to_csv(DATA_FILES["messages"], index=False)
            
            speak_msg = t["agent_speak_msg"].format(st.session_state.agent_name)
            speak_text(speak_msg, st.session_state.agent_voice_key)
            
            return t["agent_matched"].format(st.session_state.agent_name, receiver)
    return None

# 原有的 AI 函数
def ai_recognize_image(image_file, api_key, provider, lang):
    if not api_key: return {"category": t["categories"][0], "name": "-", "color": "-", "desc": "-"}
    try:
        from openai import OpenAI
        cfg = API_CONFIG[provider]
        client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
        img = Image.open(image_file); buf = BytesIO(); img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        prompt = {
            "中文": "识别图中物品，返回严格JSON：category(类别), name(名称), color(颜色), desc(特征)",
            "한국어": "사진 속 물건을 인식하고 JSON으로만 반환: category, name, color, desc",
            "English": "Identify the item in the image, return strict JSON only: category, name, color, desc"
        }[lang]
        res = client.chat.completions.create(
            model=cfg["vision_model"],
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}],
            temperature=0
        )
        return json.loads(res.choices[0].message.content)
    except Exception:
        return {"category": t["categories"][0], "name": "-", "color": "-", "desc": "-"}

def generate_post_text(info, lang, api_key, provider):
    if not api_key:
        return {
            "中文": f"【失物招领】{info['time']}在{info['location']}丢失{info['color']}{info['category']}({info['name']})，{info['desc']}。捡到请联系，感谢！",
            "한국어": f"[분실물] {info['time']} {info['location']}에서 {info['color']} {info['category']}({info['name']})을/를 잃어버렸습니다. {info['desc']}.",
            "English": f"[Lost] Lost a {info['color']} {info['category']} ({info['name']}) at {info['location']} in the {info['time']}. {info['desc']}.",
        }[lang]
    try:
        from openai import OpenAI
        cfg = API_CONFIG[provider]
        client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
        res = client.chat.completions.create(
            model=cfg["text_model"],
            messages=[{"role": "user", "content": f"写一段得体的校园失物招领文案，信息：{info}，语言：{lang}"}]
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return generate_post_text(info, lang, "", provider)

# ===================== 侧边栏 =====================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.selectbox(
        t["theme_label"], options=THEME_KEYS, format_func=lambda x: THEME_NAMES[st.session_state.lang][x],
        key="theme_select", index=THEME_KEYS.index(st.session_state.theme),
        on_change=lambda: setattr(st.session_state, "theme", st.session_state.theme_select)
    )
    st.selectbox(
        t["lang_label"], options=["中文", "한국어", "English"], label_visibility="collapsed", key="lang_select",
        index=["中文", "한국어", "English"].index(st.session_state.lang),
        on_change=lambda: setattr(st.session_state, "lang", st.session_state.lang_select)
    )
    st.selectbox(
        t["api_provider"], options=["Groq", "OpenAI"], key="api_provider_select",
        index=["Groq", "OpenAI"].index(st.session_state.api_provider),
        on_change=lambda: setattr(st.session_state, "api_provider", st.session_state.api_provider_select)
    )
    if "GROQ_API_KEY" in st.secrets:
    st.session_state.api_key = st.secrets["GROQ_API_KEY"]
    st.success("✅ API 密钥已安全配置")
else:
    st.session_state.api_key = st.text_input(t["api_key"], type="password", value="")
    
    st.divider()
    
    # Agent 配置区域
    with st.expander(t["agent_settings"], expanded=True):
        # 渲染顶部卡片（区分图片或Emoji）
        card_html = f"<div class='agent-card'>"
        if st.session_state.agent_avatar_img:
            card_html += f"<img src='{st.session_state.agent_avatar_img}' class='agent-avatar-img'>"
        else:
            card_html += f"<div class='agent-avatar-emoji'>{st.session_state.agent_avatar_emoji}</div>"
        card_html += f"<b>{st.session_state.agent_name}</b></div>"
        st.markdown(card_html, unsafe_allow_html=True)
        
        st.session_state.agent_name = st.text_input(t["agent_name"], value=st.session_state.agent_name)
        
        # 选择表情或上传图片
        emojis = ["🤖", "👽", "🦊", "🧙‍♂️", "🐱", "🤵", "🐶", "🦉", "👻", "🐼", "🦁", "🐧", "🐰", "🐻"]
        st.session_state.agent_avatar_emoji = st.selectbox(t["agent_avatar_emoji"], emojis, index=emojis.index(st.session_state.agent_avatar_emoji))
        
        agent_img_file = st.file_uploader(t["agent_avatar_upload"], type=["jpg", "png", "jpeg"])
        if agent_img_file:
            st.session_state.agent_avatar_img = encode_avatar(agent_img_file)
            st.rerun()
            
        if st.session_state.agent_avatar_img:
            if st.button(t["agent_clear_avatar"], use_container_width=True):
                st.session_state.agent_avatar_img = None
                st.rerun()
                
        voice_opts = [t["agent_voice_machine"], t["agent_voice_girl"], t["agent_voice_boy"]]
        voice_keys = ["agent_voice_machine", "agent_voice_girl", "agent_voice_boy"]
        cur_voice_idx = voice_keys.index(st.session_state.agent_voice_key)
        
        sel_voice = st.selectbox(t["agent_voice"], voice_opts, index=cur_voice_idx)
        st.session_state.agent_voice_key = voice_keys[voice_opts.index(sel_voice)]

    st.divider()
    
    if st.button(t["nav_home"], use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button(t["nav_lost"], use_container_width=True): st.session_state.page = "lost"; st.rerun()
    if st.button(t["nav_browse"], use_container_width=True): st.session_state.page = "lost_browse"; st.rerun()
    if st.button(t["nav_forum"], use_container_width=True): st.session_state.page = "forum"; st.rerun()
    if st.button(t["nav_members"], use_container_width=True): st.session_state.page = "members"; st.rerun()
    if st.session_state.logged_in:
        if st.button(t["nav_profile"], use_container_width=True): st.session_state.page = "profile"; st.rerun()
        if st.button(t["nav_msg"], use_container_width=True): st.session_state.page = "messages"; st.rerun()
        if st.button(t["nav_logout"], use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "home"
            st.rerun()
    else:
        if st.button(t["nav_login"], use_container_width=True): st.session_state.page = "login"; st.rerun()

# ===================== 登录页 =====================
def page_login():
    st.title(t["login_title"])
    tab1, tab2, tab3 = st.tabs([t["login_title"], t["reg_title"], t["find_pwd"]])
    with tab1:
        u = st.text_input(t["username"], key="login_u")
        p = st.text_input(t["password"], type="password", key="login_p")
        st.checkbox(t["remember"], key="login_remember")
        if st.button(t["login_btn"], type="primary", key="login_btn"):
            users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
            if u in users["username"].values:
                if users[users["username"] == u].iloc[0]["password"] == hash_pwd(p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.success("Login Success")
                    st.session_state.page = "home"
                    st.rerun()
                else: st.error("Wrong password")
            else: st.error("Account not found")
    with tab2:
        nu = st.text_input(t["username"], key="reg_u")
        np1 = st.text_input(t["password"], type="password", key="reg_p")
        np2 = st.text_input(t["pwd_confirm"], type="password", key="reg_c")
        nm = st.text_input(t["name"], key="reg_n")
        if st.button(t["reg_btn"], type="primary", key="reg_btn"):
            users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
            if not nu.strip() or not np1: st.error("Username/Password required")
            elif len(np1) < 6: st.error(t["pwd_length_hint"])
            elif nu in users["username"].values: st.error("Username exists")
            elif np1 != np2: st.error("Passwords mismatch")
            else:
                pd.concat([users, pd.DataFrame([{"username": nu, "password": hash_pwd(np1),
                    "name": nm, "age": "", "signature": "", "avatar": ""}])], ignore_index=True
                ).to_csv(DATA_FILES["users"], index=False)
                st.success("Registered successfully, please login.")
    with tab3:
        ru = st.text_input(t["username"], key="reset_u")
        rp = st.text_input("New " + t["password"], type="password", key="reset_p")
        if st.button(t["reset_pwd"], type="primary", key="reset_btn"):
            users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
            if ru not in users["username"].values: st.error("Account not found")
            elif len(rp) < 6: st.error(t["pwd_length_hint"])
            else:
                users.loc[users["username"] == ru, "password"] = hash_pwd(rp)
                users.to_csv(DATA_FILES["users"], index=False)
                st.success("Password reset")

# ===================== 首页 =====================
def page_home():
    # 根据是否有自定义图片渲染主页面文字
    agent_display = f"<img src='{st.session_state.agent_avatar_img}' style='width:24px; height:24px; border-radius:50%; vertical-align:middle;'>" if st.session_state.agent_avatar_img else f"<span style='font-size:1.2rem;'>{st.session_state.agent_avatar_emoji}</span>"

    st.markdown(f"""
    <div class='hero-card'>
        <div class='hero-kicker'>{t['hero_kicker']}</div>
        <h1>{t['hero_title']}</h1>
        <p style='font-size: 1.1rem; color: #ffd700; font-weight: bold;'>💡 {t.get('pain_point', '学生在遗失物品时，因为信息差和线下奔波，付出了每天数小时的精力和极度焦虑的隐性成本。')}</p>
        <p>{t['hero_desc']} <br> {agent_display} <b>{st.session_state.agent_name}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"<div class='feature-card'><h3>{t['feature_lost']}</h3><p>{t['feature_lost_desc']}</p></div>", unsafe_allow_html=True)
        if st.button(t["nav_browse"], key="home_browse"):
            st.session_state.page = "lost_browse"
            st.rerun()
        if st.button(t["lost_tab1"], key="home_post_lost"):
            st.session_state.page = "lost"
            st.rerun()
    with c2:
        st.markdown(f"<div class='feature-card'><h3>{t['feature_forum']}</h3><p>{t['feature_forum_desc']}</p></div>", unsafe_allow_html=True)
        if st.button(t["nav_forum"], key="home_forum"):
            st.session_state.page = "forum"
            st.rerun()
            
    st.divider()
    st.subheader(t["campus_stats"])
    try:
        pc = len(pd.read_csv(DATA_FILES["posts"], dtype=str))
        ic = len(pd.read_csv(DATA_FILES["lost_items"], dtype=str))
        mc = len(pd.read_csv(DATA_FILES["users"], dtype=str))
    except Exception:
        pc, ic, mc = 0, 0, 0
    a, b, c = st.columns(3)
    a.metric(t["stat_posts"], f"{pc}")
    b.metric(t["stat_items"], f"{ic}")
    c.metric(t["stat_members"], f"{mc}")
    with a:
        if st.button(t["open_posts"], key="home_go_forum", use_container_width=True):
            st.session_state.page = "forum"
            st.rerun()
    with b:
        if st.button(t["find_items"], key="home_go_items", use_container_width=True):
            st.session_state.page = "lost_browse"
            st.rerun()
    with c:
        if st.button(t["view_members"], key="home_go_members", use_container_width=True):
            st.session_state.page = "members"
            st.rerun()
    st.caption(t["data_note"])

# ===================== 浏览失物 =====================
def page_lost_browse():
    st.title(t["browse_title"])
    st.caption(t["browse_desc"])
    items = pd.read_csv(DATA_FILES["lost_items"], dtype=str).fillna("")
    if items.empty:
        st.info(t["no_data"])
        return
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        tf = st.selectbox(t["filter_type"], [t["filter_all"], t["filter_lost"], t["filter_found"]], key="bl_type")
    with f2:
        cats = sorted([str(v) for v in items["category"].unique() if str(v).strip()])
        cf = st.selectbox(t["filter_category"], [t["filter_all"]] + cats, key="bl_cat")
    with f3:
        q = st.text_input("", placeholder=t["search_placeholder"], key="bl_q")
    d = items.copy()
    if tf == t["filter_lost"]: d = d[d["type"] == "lost"]
    elif tf == t["filter_found"]: d = d[d["type"] == "found"]
    if cf != t["filter_all"]: d = d[d["category"] == cf]
    if q.strip():
        cols = [c for c in ["item_name", "category", "color", "location", "time", "desc", "owner"] if c in d.columns]
        m = d[cols].astype(str).apply(lambda col: col.str.contains(q.strip(), case=False, na=False)).any(axis=1)
        d = d[m]
    st.caption(t["result_count"].format(len(d)))
    if d.empty:
        st.info(t["no_result"])
        return
    for _, it in d.sort_values("id", ascending=False).iterrows():
        kind = t["filter_lost"] if str(it.get("type", "")) == "lost" else t["filter_found"]
        nm = str(it.get("item_name", "") or "").strip()
        head = f"{kind} · {nm + ' · ' if nm else ''}{it.get('category', '')} · {it.get('location', '')} · {it.get('time', '')}"
        with st.expander(head):
            a, b = st.columns([3, 1])
            with a:
                st.markdown(f"**{t['item_name_label']}：** {nm or '-'}")
                st.markdown(f"**{t['color_label_full']}：** {it.get('color', '-') or '-'}")
                st.markdown(f"**{t['desc_label_full']}：** {it.get('desc', '-') or '-'}")
                if it.get("contact"): st.markdown(f"**{t['contact_label_full']}：** {it.get('contact')}")
            with b:
                st.markdown(f"**{t['owner_label']}：** {it.get('owner', '-') or '-'}")
                st.markdown(f"**{t['status_label']}：** {it.get('status', 'open') or 'open'}")

# ===================== 成员页 =====================
def page_members():
    st.title(t["members_title"])
    users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
    st.caption(t["members_count"].format(len(users)))
    if users.empty:
        st.info(t["no_members"])
        return
    s = st.text_input(t["member_search"], placeholder=t["member_search_ph"], key="mem_search")
    if s.strip():
        m = users[["username", "name"]].astype(str).apply(
            lambda col: col.str.contains(s.strip(), case=False, na=False)).any(axis=1)
        users = users[m]
    if users.empty:
        st.info(t["no_member_result"])
        return
    for _, u in users.iterrows():
        a, b = st.columns([1, 9])
        with a:
            av = get_user_avatar(u.get("username", ""))
            if av is not None: st.image(av, width=56)
            else: st.markdown("### 👤")
        with b:
            dn = u.get("name", "") or u.get("username", "")
            st.markdown(f"**{dn}**　@{u.get('username', '')}")
            if u.get("signature"): st.caption(u["signature"])
        st.divider()

# ===================== 失物招领页 =====================
def page_lost():
    st.title(t["nav_lost"])
    if not st.session_state.logged_in:
        st.warning(t["not_login"])
        return
        
    agent_display = f"<img src='{st.session_state.agent_avatar_img}' style='width:24px; height:24px; border-radius:50%; vertical-align:middle;'>" if st.session_state.agent_avatar_img else f"<span style='font-size:1.2rem;'>{st.session_state.agent_avatar_emoji}</span>"
    st.markdown(f"**{agent_display} {st.session_state.agent_name}：** {t['agent_greeting_lost']}", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([t["lost_tab1"], t["lost_tab2"]])
    with tab1:
        up = st.file_uploader(t["upload_photo"], type=["jpg", "png"], key="lost_up")
        if up and st.button(t["ai_recognize"], key="lost_ai_btn"):
            with st.spinner("AI Identifying..."):
                st.session_state.ai_result = ai_recognize_image(up, st.session_state.api_key, st.session_state.api_provider, st.session_state.lang)
            st.rerun()
        ar = st.session_state.get("ai_result") or {}
        dc = ar.get("category", t["categories"][0])
        ci = t["categories"].index(dc) if dc in t["categories"] else 0
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox(t["cat_label"], t["categories"], index=ci, key="lost_cat")
            color = st.selectbox(t["color_label"], ["白色", "黑色", "蓝色", "棕色", "银色", "其他"], key="lost_color")
        with c2:
            loc = st.selectbox(t["loc_label"], LOCATIONS[st.session_state.lang], key="lost_loc")
            tm = st.selectbox(t["time_label"], t["time_opts"], key="lost_time")
        nm = st.text_input(t["item_name"], value=str(ar.get("name", "") or ""), key="lost_name")
        ds = st.text_area(t["desc_label"], value=str(ar.get("desc", "") or ""), height=80, key="lost_desc")
        ct = st.text_input(t["contact_label"], key="lost_contact")
        
        if st.button(t["submit_btn"], type="primary", key="lost_submit"):
            items = pd.read_csv(DATA_FILES["lost_items"], dtype=str).fillna("")
            nid = str(len(items) + 1)
            pd.concat([items, pd.DataFrame([{"id": nid, "type": "lost", "item_name": nm, "category": cat,
                "color": color, "location": loc, "time": tm, "desc": ds, "contact": ct,
                "owner": st.session_state.username, "status": "open"}])], ignore_index=True
            ).to_csv(DATA_FILES["lost_items"], index=False)
            posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("")
            pid = str(len(posts) + 1)
            title = f"[{t['type_lost']}] {nm} - {loc}"
            content = f"{t['cat_label']}: {cat}\n{t['color_label']}: {color}\n{t['time_label']}: {tm}\n\n{ds}\n\n{t['contact_label']}: {ct if ct else 'DM'}"
            pd.concat([posts, pd.DataFrame([{"id": pid, "title": title, "content": content, "media": "",
                "author": st.session_state.username, "time": str(pd.Timestamp.now()), "comments": "[]",
                "type": "lost", "ref_id": nid, "likes": "0", "collects": "0"}])], ignore_index=True
            ).to_csv(DATA_FILES["posts"], index=False)
            
            info = {"category": cat, "name": nm, "color": color, "location": loc, "time": tm, "desc": ds}
            
            # 👉 触发 AI 智能体匹配
            match_res = ai_smart_match_and_notify(info, "lost", st.session_state.username)
            
            txt = generate_post_text(info, st.session_state.lang, st.session_state.api_key, st.session_state.api_provider)
            st.session_state.submit_result = {"success": True, "info": info, "post_text": txt, "match_res": match_res}
            st.session_state.ai_result = None
            st.session_state.page = "lost_result"
            st.rerun()

    with tab2:
        st.file_uploader(t["upload_photo"], type=["jpg", "png"], key="found_up")
        c1, c2 = st.columns(2)
        with c1:
            cat2 = st.selectbox(t["cat_label"], t["categories"], key="found_cat")
            col2 = st.selectbox(t["color_label"], ["白色", "黑色", "蓝色", "棕色", "银色", "其他"], key="found_color")
        with c2:
            loc2 = st.selectbox(t["loc_label"], LOCATIONS[st.session_state.lang], key="found_loc")
            tm2 = st.selectbox(t["time_label"], t["time_opts"], key="found_time")
        nm2 = st.text_input(t["item_name"], key="found_name")
        ds2 = st.text_area(t["desc_label"], height=80, key="found_desc")
        
        if st.button(t["submit_btn"], type="primary", key="found_submit"):
            items = pd.read_csv(DATA_FILES["lost_items"], dtype=str).fillna("")
            nid = str(len(items) + 1)
            pd.concat([items, pd.DataFrame([{"id": nid, "type": "found", "item_name": nm2, "category": cat2,
                "color": col2, "location": loc2, "time": tm2, "desc": ds2, "contact": "",
                "owner": st.session_state.username, "status": "open"}])], ignore_index=True
            ).to_csv(DATA_FILES["lost_items"], index=False)
            posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("")
            pid = str(len(posts) + 1)
            title = f"[{t['type_found']}] {nm2} - {loc2}"
            content = f"{t['cat_label']}: {cat2}\n{t['color_label']}: {col2}\n{t['time_label']}: {tm2}\n\n{ds2}\n\nDM to claim"
            pd.concat([posts, pd.DataFrame([{"id": pid, "title": title, "content": content, "media": "",
                "author": st.session_state.username, "time": str(pd.Timestamp.now()), "comments": "[]",
                "type": "found", "ref_id": nid, "likes": "0", "collects": "0"}])], ignore_index=True
            ).to_csv(DATA_FILES["posts"], index=False)
            
            info = {"category": cat2, "name": nm2, "color": col2, "location": loc2, "time": tm2, "desc": ds2}
            # 👉 捡到东西同样触发 AI 智能体
            match_res = ai_smart_match_and_notify(info, "found", st.session_state.username)
            
            st.success(t["submit_success"])
            if match_res: st.success(match_res)
            else: st.info(t["agent_monitoring"].format(st.session_state.agent_name))

# ===================== 提交结果 =====================
def page_lost_result():
    res = st.session_state.get("submit_result")
    if not res:
        st.session_state.page = "lost"
        st.rerun()
        return
    st.success(t["submit_success"])
    
    if res.get("match_res"):
        st.markdown(f"""
        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50; margin-top: 10px;'>
            <h4 style='color: #2e7d32; margin: 0;'>{t['agent_intervened']}</h4>
            <p style='color: #1b5e20; margin-top: 5px;'>{res['match_res']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(t["agent_monitoring"].format(st.session_state.agent_name))
        
    st.divider()
    st.subheader(t["match_result"])
    items = pd.read_csv(DATA_FILES["lost_items"], dtype=str).fillna("")
    fi = items[items["type"] == "found"].copy()
    if not fi.empty:
        sc = []
        for _, r in fi.iterrows():
            s = 0
            if r["category"] == res["info"]["category"]: s += 40
            if r["color"] == res["info"]["color"]: s += 30
            if r["location"] == res["info"]["location"]: s += 30
            sc.append(s)
        fi["match"] = sc
        st.dataframe(fi.sort_values("match", ascending=False).head(3), use_container_width=True, hide_index=True)
    st.divider()
    st.subheader(t["post_generated"])
    st.info(res["post_text"])
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t["back_login"], key="res_back"): # 借用返回键
            st.session_state.page = "lost"
            st.rerun()
    with c2:
        if st.button(t["nav_forum"], key="res_forum"):
            st.session_state.page = "forum"
            st.rerun()

# ===================== 帖子渲染组件 =====================
def render_post(post, is_owner, scope="forum"):
    post_id = str(post["id"])
    uid = f"{scope}_{post_id}"
    a, b = st.columns([1, 9])
    
    with a:
        av = get_user_avatar(str(post["author"]))
        if av is not None: st.image(av, width=64)
        else: st.caption("👤")
            
    with b:
        try: editing = st.session_state.editing_post is not None and int(float(st.session_state.editing_post)) == int(float(post_id))
        except (ValueError, TypeError): editing = False
            
        if editing:
            et = st.text_input(t["post_title"], value=str(post["title"]), key=f"et_{uid}")
            ec = st.text_area(t["post_content"], value=str(post["content"]), key=f"ec_{uid}")
            x, y = st.columns(2)
            with x:
                if st.button(t["save_edit"], key=f"save_{uid}", type="primary"):
                    posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("")
                    posts.loc[posts["id"] == post_id, "title"] = et
                    posts.loc[posts["id"] == post_id, "content"] = ec
                    posts.to_csv(DATA_FILES["posts"], index=False)
                    st.session_state.editing_post = None
                    st.success("Saved")
                    st.rerun()
            with y:
                if st.button(t["cancel_edit"], key=f"cancel_edit_{uid}"):
                    st.session_state.editing_post = None
                    st.rerun()
        else:
            tag = ""
            pt = str(post.get("type", ""))
            if pt == "lost": tag = f"**[{t['type_lost']}]** "
            elif pt == "found": tag = f"**[{t['type_found']}]** "
            st.markdown(f"<div class='card'>{tag}<h4>{post['title']}</h4>"
                        f"<p style='white-space: pre-line;'>{post['content']}</p>"
                        f"<small>{t['owner_label']}：{post['author']} · {post['time']}</small></div>",
                        unsafe_allow_html=True)
            mf = str(post.get("media", "") or "")
            if mf:
                mp = os.path.join("media", mf)
                if os.path.exists(mp):
                    ext = os.path.splitext(mf)[1].lower()
                    if ext in (".jpg", ".jpeg", ".png", ".gif"): st.image(mp, use_column_width=True)
                    elif ext in (".mp4", ".mov"): st.video(mp)
                    elif ext in (".mp3", ".wav", ".ogg"): st.audio(mp)
                        
            try: lc = int(float(post.get("likes", 0)))
            except (ValueError, TypeError): lc = 0
            try: cc = int(float(post.get("collects", 0)))
            except (ValueError, TypeError): cc = 0
                
            if st.session_state.logged_in:
                liked = is_liked(st.session_state.username, post_id)
                col_ = is_collected(st.session_state.username, post_id)
                x, y = st.columns(2)
                with x:
                    if st.button(f"❤️ {t['liked'] if liked else t['like']} ({lc})", key=f"like_{uid}"):
                        toggle_like(st.session_state.username, post_id); st.rerun()
                with y:
                    if st.button(f"⭐ {t['collected'] if col_ else t['collect']} ({cc})", key=f"collect_{uid}"):
                        toggle_collect(st.session_state.username, post_id); st.rerun()
            else:
                st.caption(f"❤️ {lc}　⭐ {cc}　·　{t['guest_interact_tip']}")
                
            if is_owner:
                x, y = st.columns(2)
                with x:
                    if st.button(t["edit_post"], key=f"edit_{uid}"):
                        try: st.session_state.editing_post = int(float(post_id))
                        except (ValueError, TypeError): pass
                        st.rerun()
                with y:
                    if st.button(t["delete_post"], key=f"del_{uid}"):
                        try: st.session_state.confirm_delete_post = int(float(post_id))
                        except (ValueError, TypeError): pass
                        st.rerun()
                        
            try: confirming = st.session_state.confirm_delete_post is not None and int(float(st.session_state.confirm_delete_post)) == int(float(post_id))
            except (ValueError, TypeError): confirming = False
                
            if confirming:
                st.warning(t["delete_confirm"])
                x, y = st.columns(2)
                with x:
                    if st.button("Confirm Delete", key=f"cdel_{uid}", type="primary"):
                        latest = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("")
                        tgt = latest[latest["id"] == post_id]
                        if not tgt.empty and str(tgt.iloc[0]["author"]) == str(st.session_state.username):
                            latest = latest[latest["id"] != post_id]
                            latest.to_csv(DATA_FILES["posts"], index=False)
                            tm = str(tgt.iloc[0].get("media", "") or "")
                            if tm:
                                safe = os.path.basename(tm)
                                fpath = os.path.join("media", safe)
                                if os.path.isfile(fpath):
                                    try: os.remove(fpath)
                                    except OSError: pass
                            st.success(t["deleted"])
                        else: st.error(t["no_permission"])
                        st.session_state.confirm_delete_post = None
                        st.rerun()
                with y:
                    if st.button(t["cancel_edit"], key=f"cdel_cancel_{uid}"):
                        st.session_state.confirm_delete_post = None
                        st.rerun()
                        
    try:
        comments = json.loads(post["comments"]) if pd.notna(post["comments"]) else []
        if not isinstance(comments, list): comments = []
    except (TypeError, ValueError): comments = []
        
    with st.expander(f"💬 {len(comments)} {t['comment_btn']}"):
        for c in comments:
            cu = str(c.get("user", "Anonymous"))
            cav = get_user_avatar(cu)
            x, y = st.columns([1, 12])
            with x:
                if cav is not None: st.image(cav, width=36)
                else: st.caption("👤")
            with y: st.caption(f"{cu}: {c.get('text', '')}")
                
        if st.session_state.logged_in:
            nc = st.text_input(t["comment_placeholder"], key=f"cmt_{uid}")
            if st.button(t["comment_btn"], key=f"cmt_btn_{uid}"):
                if not nc.strip(): st.warning("Cannot be empty")
                else:
                    posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("")
                    comments.append({"user": st.session_state.username, "text": nc.strip(), "time": str(pd.Timestamp.now())})
                    posts.loc[posts["id"] == post_id, "comments"] = json.dumps(comments, ensure_ascii=False)
                    posts.to_csv(DATA_FILES["posts"], index=False)
                    st.rerun()
        else:
            st.caption(t["guest_comment_tip"])
    st.divider()

# ===================== 论坛页 =====================
def page_forum():
    st.title(t["forum_title"])
    posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("").sort_values("id", ascending=False)
    st.caption(t["forum_desc"].format(len(posts)))
    if st.session_state.logged_in:
        with st.expander(t["new_post"], expanded=False):
            title = st.text_input(t["post_title"], key="fp_title")
            content = st.text_area(t["post_content"], height=100, key="fp_content")
            mf = st.file_uploader(
                t["media_upload"],
                type=["jpg", "jpeg", "png", "gif", "mp4", "mov", "mp3", "wav", "ogg"],
                help=t["media_upload_help"], key="fp_media"
            )
            if st.button(t["post_btn"], type="primary", key="fp_submit"):
                nid = str(len(posts) + 1)
                mn = save_media_file(mf, nid) if mf else ""
                pd.concat([posts, pd.DataFrame([{"id": nid, "title": title, "content": content, "media": mn,
                    "author": st.session_state.username, "time": str(pd.Timestamp.now()),
                    "comments": "[]", "type": "normal", "ref_id": "", "likes": "0", "collects": "0"}])],
                    ignore_index=True).to_csv(DATA_FILES["posts"], index=False)
                st.success("Success")
                st.rerun()
    else:
        st.info(t["guest_tip"])
    st.divider()
    
    if posts.empty:
        st.info(t["empty_forum"])
        return
    for _, p in posts.iterrows():
        render_post(p, str(p["author"]) == str(st.session_state.username), scope="forum")

# ===================== 个人中心 =====================
def page_profile():
    st.title(t["profile_title"])
    users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
    m = users[users["username"] == st.session_state.username]
    if m.empty:
        st.error("User not found")
        return
    user = m.iloc[0]

    tab_info, tab_my_posts, tab_my_likes, tab_my_collects = st.tabs([t["profile_title"], t["my_posts"], t["my_likes"], t["my_collects"]])

    with tab_info:
        c1, c2 = st.columns([1, 2])
        with c1:
            af = st.file_uploader(t["avatar"], type=["jpg", "jpeg", "png", "webp", "gif", "bmp"], key="prof_avatar")
            cur = get_user_avatar(st.session_state.username)
            if cur is not None and not af: st.image(cur, width=150)
            st.caption(t["avatar_tip"])
        with c2:
            nm = st.text_input(t["name"], value=str(user["name"]) if pd.notna(user["name"]) else "", key="prof_name")
            ag = st.text_input(t["age"], value=str(user["age"]) if pd.notna(user["age"]) else "", key="prof_age")
            sg = st.text_input(t["signature"], value=str(user["signature"]) if pd.notna(user["signature"]) else "", key="prof_sig")
            if st.button(t["save_btn"], type="primary", key="prof_save"):
                b64 = ""
                if af:
                    try: b64 = encode_avatar(af)
                    except Exception as e:
                        st.error(f"Avatar Error: {e}"); return
                idx = users[users["username"] == st.session_state.username].index[0]
                users.at[idx, "name"] = nm
                users.at[idx, "age"] = ag
                users.at[idx, "signature"] = sg
                if b64: users.at[idx, "avatar"] = b64
                users.to_csv(DATA_FILES["users"], index=False)
                st.success("Saved")
                st.rerun()

    all_posts = pd.read_csv(DATA_FILES["posts"], dtype=str).fillna("").sort_values("id", ascending=False)

    with tab_my_posts:
        mp = all_posts[all_posts["author"] == st.session_state.username]
        if mp.empty: st.caption(t["empty_posts"])
        else:
            for _, p in mp.iterrows(): render_post(p, True, scope="prof_posts")

    with tab_my_likes:
        rel = _read_rel(DATA_FILES["likes"])
        ml = rel[rel["username"] == st.session_state.username]
        if ml.empty: st.caption(t["empty_likes"])
        else:
            for _, r in ml.iterrows():
                mlist = all_posts[all_posts["id"] == str(r["post_id"])]
                if not mlist.empty:
                    p = mlist.iloc[0]
                    render_post(p, str(p["author"]) == str(st.session_state.username), scope="prof_likes")

    with tab_my_collects:
        rel = _read_rel(DATA_FILES["collects"])
        mc = rel[rel["username"] == st.session_state.username]
        if mc.empty: st.caption(t["empty_collects"])
        else:
            for _, r in mc.iterrows():
                mlist = all_posts[all_posts["id"] == str(r["post_id"])]
                if not mlist.empty:
                    p = mlist.iloc[0]
                    render_post(p, str(p["author"]) == str(st.session_state.username), scope="prof_collects")

# ===================== 站内消息 =====================
def page_messages():
    st.title(t["msg_title"])
    if not st.session_state.logged_in:
        st.warning(t["not_login"])
        return
    users = pd.read_csv(DATA_FILES["users"], dtype=str).fillna("")
    others = sorted([u for u in users["username"].tolist() if u and u != st.session_state.username])
    if not others:
        st.info(t["no_members_tip"])
        return
    sel = st.selectbox(t["send_to"], others, key="chat_sel")
    msgs = pd.read_csv(DATA_FILES["messages"], dtype=str).fillna("")
    conv = msgs[
        ((msgs["sender"] == st.session_state.username) & (msgs["receiver"] == sel)) |
        ((msgs["sender"] == sel) & (msgs["receiver"] == st.session_state.username))
    ].copy()
    if not conv.empty:
        conv["_sid"] = pd.to_numeric(conv["id"], errors="coerce").fillna(0)
        conv = conv.sort_values("_sid")
        st.caption(t["chat_history"].format(sel))
        for _, msg in conv.iterrows():
            mine = msg["sender"] == st.session_state.username
            with st.chat_message("user" if mine else "assistant"):
                st.caption(("" if mine else t["from"] + ": " + msg["sender"] + " · ") + str(msg.get("time", "")))
                st.write(str(msg.get("content", "")))
    else:
        st.info(t["no_chat"].format(sel))
        
    with st.form("send_msg_form", clear_on_submit=True):
        body = st.text_area("", placeholder=t["msg_placeholder"], height=90, key="msg_body")
        sent = st.form_submit_button(t["send_btn"], type="primary")
        if sent:
            if not body.strip(): st.warning("Empty message")
            else:
                latest = pd.read_csv(DATA_FILES["messages"], dtype=str).fillna("")
                ids = pd.to_numeric(latest.get("id", pd.Series(dtype=float)), errors="coerce")
                nid = str(int(ids.max()) + 1) if not ids.empty and ids.notna().any() else "1"
                pd.concat([latest, pd.DataFrame([{"id": nid, "sender": st.session_state.username,
                    "receiver": sel, "content": body.strip(), "time": str(pd.Timestamp.now())}])],
                    ignore_index=True).to_csv(DATA_FILES["messages"], index=False)
                st.rerun()
                
    st.divider()
    st.subheader(t["inbox"] + " / " + t["sent"])
    ti, to_ = st.tabs([t["inbox"], t["sent"]])
    with ti:
        ib = msgs[msgs["receiver"] == st.session_state.username].sort_values("id", ascending=False)
        if ib.empty: st.caption(t["empty_inbox"])
        else:
            for _, m in ib.iterrows():
                st.markdown(f"**{t['from']}：{m['sender']}** · {m['time']}")
                st.write(m["content"])
                st.divider()
    with to_:
        ob = msgs[msgs["sender"] == st.session_state.username].sort_values("id", ascending=False)
        if ob.empty: st.caption(t["empty_sent"])
        else:
            for _, m in ob.iterrows():
                st.markdown(f"**{t['to']}：{m['receiver']}** · {m['time']}")
                st.write(m["content"])
                st.divider()

# ===================== 路由 =====================
PAGES = {
    "home": page_home, "login": page_login, "lost": page_lost,
    "lost_browse": page_lost_browse, "members": page_members,
    "lost_result": page_lost_result, "forum": page_forum,
    "profile": page_profile, "messages": page_messages,
}
PAGES.get(st.session_state.page, page_home)()
