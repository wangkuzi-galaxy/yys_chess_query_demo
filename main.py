import gradio as gr
from config import base_config
import ups_response
import pandas as pd

def process_input(up_name, user_id):
    uids = base_config.base_uids.copy()
    
    if up_name.strip() or user_id.strip():
        uids.append({"name": up_name.strip(), "id": user_id.strip()})
    
    result = ups_response.process_uids_with_names(uids)
    
    # 检查是否有投注信息
    if not result["bet_details"]:
        empty_table = pd.DataFrame(columns=["UP主姓名", "竞猜阵营"])
        table_html = empty_table.to_html(index=False, classes=["table", "table-striped", "table-hover"])
        summary = result['decision']
        return table_html, summary
    
    # 创建 DataFrame
    df = pd.DataFrame(result["bet_details"])
    
    # 只保留 name 和 bet 列，并重命名
    df = df[['name', 'bet']]
    df = df.rename(columns={
        "name": "UP主姓名",
        "bet": "竞猜阵营"
    })
    
    # 将 '红方' 和 '蓝方' 映射为 '红' 和 '蓝'
    df['竞猜阵营'] = df['竞猜阵营'].map({'红方': '红', '蓝方': '蓝'})
    
    # 生成 HTML 表格
    table_html = df.to_html(index=False, classes=["table", "table-striped", "table-hover"])
    
    # 生成摘要文本
    summary = f"最终决策：{result['decision']}"
    
    return table_html, summary


def main():
    custom_css = """
    <style>
    body {
        background-color: #f0f0f0;
        font-family: Arial, sans-serif;
    }
    .gradio-container {
        max-width: 800px !important;
        margin: auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    .gradio-interface {
        background-color: #ffffff;
    }
    .gradio-input, .gradio-output {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    p {
        color: #34495e;
        text-align: center;
        margin-bottom: 20px;
    }
    .table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }
    .table th, .table td {
        padding: 0.75rem;
        vertical-align: top;
        border-top: 1px solid #dee2e6;
        text-align: center;
    }
    .table thead th {
        vertical-align: bottom;
        border-bottom: 2px solid #dee2e6;
    }
    .table-striped tbody tr:nth-of-type(odd) {
        background-color: rgba(0, 0, 0, 0.05);
    }
    .table-hover tbody tr:hover {
        background-color: rgba(0, 0, 0, 0.075);
    }
    </style>
    """

    iface = gr.Interface(
        fn=process_input,
        inputs=[
            gr.Textbox(label="额外 UP 名", placeholder="可选：输入额外 UP 名"),
            gr.Textbox(label="额外网易大神 user_id", placeholder="可选：输入额外网易大神 user_id")
        ],
        outputs=[
            gr.HTML(label="投注详情"),
            gr.Textbox(label="决策摘要")
        ],
        title="UP 主对弈竞猜阵营选择信息",
        description="已经内置 UP 主列表。也可以输入额外的 UP 名和网易大神 user_id（均可为空）来添加到分析中。",
        css=custom_css,
        allow_flagging="never",
        clear_btn="一键清除",
        submit_btn="提交信息"
    )
    
    iface.launch(server_port=7860)

if __name__ == "__main__":
    main()