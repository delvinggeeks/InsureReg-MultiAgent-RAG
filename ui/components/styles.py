"""
InsureReg - Custom CSS Styles
Premium dark-theme styling for the Streamlit application.
"""


def get_custom_css():
    """Return the complete custom CSS for InsureReg."""
    return """
    <style>
    /* ─── Import Google Font ─────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ─── Global Styles ──────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* ─── Main Header ────────────────────────────── */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1B4F8A 0%, #2E86DE 50%, #C9A227 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    
    .main-header p {
        color: #888;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }
    
    /* ─── Chat Messages ──────────────────────────── */
    .user-message {
        background: linear-gradient(135deg, #1B4F8A, #2563EB);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.75rem 0;
        font-size: 0.95rem;
        box-shadow: 0 2px 12px rgba(27, 79, 138, 0.3);
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.25rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.75rem 0;
        font-size: 0.95rem;
        backdrop-filter: blur(10px);
    }
    
    /* ─── Routing Badge ──────────────────────────── */
    .routing-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 0.25rem 0.25rem 0.25rem 0;
    }
    
    .routing-badge.group {
        background: rgba(201, 162, 39, 0.15);
        color: #C9A227;
        border: 1px solid rgba(201, 162, 39, 0.3);
    }
    
    .routing-badge.department {
        background: rgba(37, 99, 235, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(37, 99, 235, 0.3);
    }
    
    .routing-badge.confidence {
        background: rgba(34, 197, 94, 0.15);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    /* ─── Source Citation Card ────────────────────── */
    .source-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.8rem;
        transition: all 0.2s ease;
    }
    
    .source-card:hover {
        border-color: rgba(201, 162, 39, 0.3);
        background: rgba(201, 162, 39, 0.03);
    }
    
    .source-card .source-title {
        color: #C9A227;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .source-card .source-score {
        color: #4ADE80;
        font-size: 0.7rem;
        float: right;
    }
    
    .source-card .source-content {
        color: #999;
        font-size: 0.75rem;
        margin-top: 0.4rem;
        line-height: 1.4;
    }
    
    /* ─── Department Cards ───────────────────────── */
    .dept-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    
    .dept-card:hover {
        transform: translateY(-2px);
        border-color: rgba(37, 99, 235, 0.3);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    
    .dept-card .dept-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .dept-card .dept-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #E8E8E8;
    }
    
    .dept-card .dept-desc {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.5rem;
        line-height: 1.5;
    }
    
    .dept-card .dept-status {
        margin-top: 0.75rem;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .status-active {
        background: rgba(34, 197, 94, 0.1);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.2);
    }
    
    .status-empty {
        background: rgba(251, 146, 60, 0.1);
        color: #FB923C;
        border: 1px solid rgba(251, 146, 60, 0.2);
    }
    
    /* ─── Audit Log Table ────────────────────────── */
    .audit-row {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.8rem;
    }
    
    /* ─── Stats Cards ────────────────────────────── */
    .stat-card {
        background: linear-gradient(135deg, rgba(27, 79, 138, 0.2), rgba(37, 99, 235, 0.1));
        border: 1px solid rgba(37, 99, 235, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
    }
    
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #60A5FA;
    }
    
    .stat-card .stat-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.25rem;
    }
    
    /* ─── Upload Area ────────────────────────────── */
    .upload-area {
        border: 2px dashed rgba(201, 162, 39, 0.3);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background: rgba(201, 162, 39, 0.03);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: rgba(201, 162, 39, 0.6);
        background: rgba(201, 162, 39, 0.06);
    }
    
    /* ─── Streamlit Overrides ────────────────────── */
    .stChatMessage {
        background: transparent !important;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
    }
    
    /* Smooth scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    </style>
    """
