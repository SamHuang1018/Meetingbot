fetch_search_results_template = '''
                                    Summarize the following search results in a clear and concise manner in Traditional Chinese (zh-tw).
                                    Each summary should be clearly separated by numbering (1, 2, 3, etc.) and include:
                                    1.
                                    - 標題
                                    - 簡短描述 (摘要)
                                    - 連結 (link)
                                    - 完整網址
                                    - 圖片

                                    Please ensure that each summary provides the most relevant and important information from each result.
                            '''

meeting_summary_prompt_template_v1 = '''
                                    Please give me a title and write a concise meeting summary approximately 1/2 the length of the original meeting notes using zh-tw language.
                                    Structure the summary into several levels of topics and supporting details so the key discussion points and outcomes are clear and easy to reference. For each topic, include the most salient points and decisions.
                                    Focus on capturing the essential information without repetitive or unnecessary detail so readers can efficiently comprehension the discussion. Please reply in zh-tw language.
                                '''

meeting_summary_prompt_template_v2 = '''
                                    Please give me a title and write a concise meeting summary of the original meeting notes using zh-tw language.
                                    Structure the summary to include the following elements: 
                                    1. Title
                                    - A concise title reflecting the main topic or key discussion points of the meeting.
                                    2. Basic Information
                                    Include only the available information among the following:
                                    - Date
                                    - Time
                                    - Location
                                    - Attendees
                                    3. Introduction
                                    - The purpose or goal of the meeting. 
                                    4. Main Discussion Topics
                                    List all discussion topics, each topic should include the following:
                                    - Topic Overview: A brief description of the topic.
                                    - Key Discussion Points: The detailed discussion content and viewpoints.
                                    - Decisions and Action Items: Decisions made and tasks assigned, including responsible persons and deadlines.
                                    5. Summary and Next Steps
                                    - Summary of conclusions reached. 
                                    - List of follow-up actions and items to be monitored. 
                                    Focus on capturing the essential information without repetitive or unnecessary detail so readers can efficiently comprehend the discussion.
                                '''
                                
meeting_summary_prompt_template_v3 = '''
                                    請生成會議摘要，根據提供的逐字稿，會議摘要應包括以下部分並使用繁體中文回答：
                                    1. 標題
                                    - 一個簡明扼要的標題，反映會議的主要議題或關鍵討論點。
                                    2. 會議資訊
                                    - 如果有提及日期、時間、地點才列出來。如果未提供，則千萬別列出來。
                                    3. 出席者
                                    - 如果有提及出席者，包括主持人和記錄員才列出來。如果未提供，則千萬別列出來。
                                    - 提及任何缺席者。
                                    4. 引言
                                    - 會議目的或目標。
                                    5. 主要討論議題
                                    - 議題一：議題概述
                                    - 討論要點：詳細討論內容和觀點。
                                    - 決策和行動項目：做出的決策和分配的任務，包括負責人和截止日期。
                                    - 議題二：議題概述
                                    - 討論要點：詳細討論內容和觀點。
                                    - 決策和行動項目：做出的決策和分配的任務，包括負責人和截止日期。
                                    （依此類推，列出所有討論的議題）
                                    6. 總結與後續步驟
                                    - 結論總結：會議達成的結論。
                                    - 後續行動項目：需跟進的行動和項目清單。
                                '''
                                
meeting_verbatim_prompt_template_v1 = '''
                                    Please generate the title and meeting information based on the provided transcript. The record should be structured with the following sections and all the content reply in zh-tw:

                                    1. **Title**:
                                        - Create a suitable title for the meeting.
                                    2. **Meeting Information**:
                                        - Date
                                        - Time
                                        - Location
                                    3. **Attendees**:
                                        - List all attendees, including the host and note-taker.
                                        - Mention any absentees.
                                    4. **Decisions and Action Items**:
                                        - Clearly state the decisions made for each agenda item.
                                        - List any action items assigned, including responsible parties and deadlines.
                                    5. **Verbatim Transcript**:
                                '''

meeting_verbatim_prompt_template_v2 = '''
                                    請生成會議記錄，根據提供的逐字稿，會議記錄應包括以下部分並使用繁體中文回答：

                                    **標題**：
                                    - 為會議創建一個合適的標題。

                                    **會議資訊**：
                                    - 如果有提及日期、時間、地點才列出來。如果未提供，則千萬別列出來。

                                    **出席者**：
                                        - 如果有提及出席者，包括主持人和記錄員才列出來。如果未提供，則千萬別列出來。
                                        - 提及任何缺席者。

                                    **決定和行動項目**：
                                        - 明確說明對每個議程項目所做的決定。
                                        - 列出任何分配的行動項目，包括負責人和截止日期。

                                    只要顯示「**逐字稿完整如下**：」就好，不要加入任何一個字在裡面。
                                '''   
                                
relevant_suggestion_prompt_template = '''
                                    Please provide relevant suggestions based on the provided meeting summary or transcript.
                                    The suggestions should aim to improve future meetings, address any issues discussed, and propose actionable steps. Structure the suggestions into the following sections:
                                    
                                    1. **Overall Feedback**: Provide general feedback on the meeting's effectiveness, highlighting any strengths and weaknesses.
                                    2. **Specific Recommendations**: For each major topic or decision discussed, offer specific recommendations to address issues, enhance outcomes, or streamline processes.
                                    3. **Actionable Steps**: List practical steps that can be taken to implement the recommendations, including responsible parties and deadlines.
                                    Please reply in zh-tw language.
                                '''     
