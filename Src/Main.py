#https://github.com/DucHung0109/Post_News_Social

from Get_News import *
from Process_News import *
from Save_Posted_News import *
from Post_Page_Facebook import *
from pymongo.mongo_client import MongoClient
import os

# Get news from NewsAPI
news_api = os.environ["NEWS_API"]
list_news = get_news(news_api)
# Change into list of json object to input into Gemini
list_news_json = list_to_json(list_news)

# Connect to MongoDB by DataBase User
username_mongo = os.environ["USERNAME_MONGO"]
password_mongo = os.environ["PASSWORD_MONGO"]
mongo_uri = f"mongodb+srv://{username_mongo}:{password_mongo}@postednews.nm9vqhx.mongodb.net/?retryWrites=true&w=majority&appName=PostedNews"
client = MongoClient(mongo_uri)
db = client['Post_News_FanPage']
postedNews_collection = db['postedNews_collection']

# Delete articles saved more than 6 days
delete_too_late_news(postedNews_collection)

# Take posted articles
list_news_posted_json = load_news(postedNews_collection)

# Process news
my_api_key = os.environ["GEMINI_API"]
models = ["gemini-2.0-flash"]
client = genai.Client(api_key=my_api_key)

# Choose new news(unposted)
print("Choose new news")
prompt_config = """
Bạn là 1 người đọc tin tức, hãy phân biệt các tin tức có khác nhau nhiều về nội dung không.
"""
prompt =  """
    Tôi cung cấp 2 danh sách bài báo:

    1. Danh sách bài mới (list_news): mỗi phần tử gồm title, content
    2. Danh sách bài đã đăng tuần trước (posted_news): gồm title và content

    Hãy **so sánh nội dung**, không chỉ dựa vào tiêu đề. Giữ lại những bài trong list_news có nội dung KHÁC BIỆT RÕ RỆT hoặc CÓ NHỮNG THÔNG TIN MỚI mà tin tức đã đăng không có so với posted_news.

    Trả kết quả dưới dạng JSON, ví dụ:

    [
    {
        "title": "Giá xăng dầu tăng mạnh",
        "reason": "Không trùng nội dung nào trong bài đã đăng"
    },
    {
        "title": "Giá xăng dầu tăng nhẹ",
        "reason": "Có nội dung mới trong bài đã đăng"
    },
    ...
    ]
"""



list_news_postable = news_unposted(client, prompt_config, prompt, models[0], list_news_json, list_news_posted_json)

list_title = []
for item in list_news_postable:
    title = item['title']
    reason = item['reason']
    list_title.append(title)
# Remove posted news
list_news = [item for item in list_news if item.title in list_title]

# Choose top 3 hottest news
print("Choose hottest news")
prompt_config = """
    Bạn là một người đọc tin tức trên mạng xã hội, thường quan tâm đến các tin nóng liên quan đến chính trị, kinh tế, xã hội, giáo dục, y tế – những chủ đề gây tranh luận hoặc ảnh hưởng đến cuộc sống cộng đồng.

    Bạn **không quan tâm nhiều** đến các tin thể thao, giải trí, showbiz hoặc các chủ đề nhẹ nhàng.

    Bạn muốn chọn ra những bài báo có nội dung đáng chú ý, tạo được sự quan tâm và bàn luận thật sự trên mạng xã hội.

"""
prompt =  """
    Tôi cung cấp danh sách bài báo: mỗi phần tử gồm title, content.
    
    Hãy chọn ra tối đa 3 bài báo **nóng hổi**, được **quan tâm nhiều** trên mạng xã hội. Ưu tiên các chủ đề như **chính trị, kinh tế, xã hội, giáo dục, y tế** – những nội dung ảnh hưởng đến cộng đồng, có khả năng tạo thảo luận sâu.

    **Không chọn** bài viết về thể thao, giải trí, showbiz, văn hóa nghệ thuật hoặc các tin nhẹ nhàng, đời thường.

    Mỗi bài được chọn phải có **nội dung rõ ràng khác nhau** và **không chứa yếu tố phản động hoặc nhạy cảm chính trị nguy hiểm**.

    Trả kết quả về dạng JSON, ví dụ:

    [
    {
        "title": "Tên bài viết",
        "reason": "Vì sao bài này được chọn"
    },
    ...
    ]
"""

list_news_json = list_to_json(list_news)
list_news_hottest = gen_content(client, prompt_config, prompt, models[0], list_news_json)

list_title = []
for item in list_news_hottest:
    title = item['title']
    reason = item['reason']
    list_title.append(title)

list_news = [item for item in list_news if item.title in list_title]

# Generate description
print("Generate description")
prompt_config = """
    Bạn là 1 người đọc tin tức. Sau khi đọc xong, bạn sẽ tóm tắt ý chính để đăng lên mạng xã hội.
    Bạn không viết như nhà báo, mà sẽ:
        - Tóm tắt nội dung dễ hiểu, súc tích nhưng có chiều sâu
        - Nêu bật 2-3 ý chính quan trọng nhất trong bài
        - Viết sao cho người đọc cảm thấy có gì đó đáng chú ý để họ muốn bấm vào xem tiếp hoặc bình luận
        - Nếu nội dung quá ngắn, bạn có thể diễn giải thêm để làm rõ ý

    Ngắn gọn nhưng không quá cụt, nên dài khoảng 2-4 câu.
"""
prompt =  """
    Tôi cung cấp danh sách bài báo: mỗi phần tử gồm title, content

    Hãy **tóm tắt nội dung chính** của mỗi bài báo thành 1 đoạn ngắn (~2-4 câu), súc tích nhưng giàu thông tin.
    Trả kết quả về dạng JSON, ví dụ:

    [
    {
        "title": "Tên bài viết",
        "description": "Tóm tắt nội dung chính (~2-4 câu, cuốn hút, giúp người đọc hiểu nội dung và muốn bình luận)"
    },
    ...
    ]
"""

list_news_json = list_to_json(list_news)
list_news_description = gen_content(client, prompt_config, prompt, models[0], list_news_json)
for item in list_news_description:
    title = item['title']
    description = item['description']
    for news in list_news:
        if news.title == title:
            news.add_description(description)

# Generate comment
print("Generate comment")
prompt_config = """
    Bạn là một người đọc tin tức có chút hiểu biết xã hội. Sau khi đọc bài báo, bạn viết một đoạn bình luận ngắn để chia sẻ quan điểm cá nhân lên mạng xã hội.

    Cách viết:
        - Có chính kiến nhẹ hoặc đặt câu hỏi gợi mở
        - Có thể pha chút cảm xúc như bức xúc, hài hước, tò mò…
        - Dùng lời văn tự nhiên như người thật, không quá trau chuốt
        - Viết như đang đăng lên Facebook để bạn bè cùng vào bàn luận
        - Không cần khách quan tuyệt đối – bạn là người đọc, không phải nhà báo hay chuyên gia

    Tránh viết kiểu trung lập, khô khan, máy móc.
    Bình luận không nên mang yếu tố kích động, phản động, gây tranh cãi quá mức hay đưa ra thông tin sai lệch.
    Tránh khẩu hiệu, giáo điều hoặc viết như một AI. Hãy viết tự nhiên như một người Việt Nam bình thường đang bình luận trên Facebook.
"""
prompt =  """
    Tôi cung cấp danh sách bài báo: mỗi phần tử gồm title, content

    Hãy viết 1 **bình luận ngắn** (1-3 câu) thể hiện quan điểm hoặc cảm nhận của bạn về bài báo, giống như bạn chia sẻ lên Facebook để người khác vào bàn luận.
    Bình luận không nên mang yếu tố kích động, phản động, gây tranh cãi quá mức hay đưa ra thông tin sai lệch.
    Tránh khẩu hiệu, giáo điều hoặc viết như một AI. Hãy viết tự nhiên như một người Việt Nam bình thường đang bình luận trên Facebook.
    Trả kết quả về dạng JSON, ví dụ:

    [
    {
        "title": "Tên bài viết",
        "comment": "Bình luận của bạn về bài viết"
    },
    ...
    ]
"""

list_news_comment = gen_content(client, prompt_config, prompt, models[0], list_news_json)
for item in list_news_comment:
    title = item['title']
    comment = item['comment']
    for news in list_news:
        if news.title == title:
            news.add_comment(comment)

# Generate content_vn
print("Generate content_vn and title_vn")
prompt_config = """
    Bạn là 1 người phiên dịch tin tức chuyên nghiệp, có kiến thức chuyên môn. Hãy dịch nội dung bài báo từ tiếng anh sang tiếng việt.
"""
prompt =  """
    Tôi cung cấp danh sách bài báo: mỗi phần tử gồm title, content

    Hãy **dịch tiêu đề** và **dịch toàn bộ nội dung** của mỗi bài báo từ tiếng anh sang tiếng việt
    Trả kết quả về dạng JSON, ví dụ:

    [
    {
        "title": "Tên bài viết",
        "title_vn": "Tiêu đề tiếng việt của bài viết",
        "content_vn": "Nội dung tiếng việt của bài viết"
    },
    ...
    ]
"""

list_news_content_vn = gen_content(client, prompt_config, prompt, models[0], list_news_json)

for item in list_news_content_vn:
    title = item['title']
    content_vn = item['content_vn']
    title_vn = item['title_vn']
    for news in list_news:
        if news.title == title:
            news.add_content_vn(content_vn)
            news.add_title_vn(title_vn)

# Generate general comment
print("Generate general comment")
prompt_config = """
    Bạn là một người đọc tin tức có chút hiểu biết xã hội. Sau khi đọc bài báo, bạn viết một đoạn bình luận ngắn để chia sẻ quan điểm cá nhân lên mạng xã hội.

    Cách viết:
        - Có chính kiến nhẹ hoặc đặt câu hỏi gợi mở
        - Có thể pha chút cảm xúc như bức xúc, hài hước, tò mò…
        - Dùng lời văn tự nhiên như người thật, không quá trau chuốt
        - Viết như đang đăng lên Facebook để bạn bè cùng vào bàn luận
        - Không cần khách quan tuyệt đối – bạn là người đọc, không phải nhà báo hay chuyên gia

    Tránh viết kiểu trung lập, khô khan, máy móc.
    Bình luận không nên mang yếu tố kích động, phản động, gây tranh cãi quá mức hay đưa ra thông tin sai lệch.
    Tránh khẩu hiệu, giáo điều hoặc viết như một AI. Hãy viết tự nhiên như một người Việt Nam bình thường đang bình luận trên Facebook.
"""
prompt =  """
    Tôi cung cấp danh sách bài báo: mỗi phần tử gồm title, content

    Hãy viết 1 **bình luận ngắn** (1-3 câu) thể hiện quan điểm hoặc cảm nhận của bạn về **toàn bộ các bài báo, toàn bộ tình hình, thay đổi nổi bật trong ngày qua"",
    giống như bạn chia sẻ lên Facebook để người khác vào bàn luận.
    
    Bình luận không nên mang yếu tố kích động, phản động, gây tranh cãi quá mức hay đưa ra thông tin sai lệch.
    Tránh khẩu hiệu, giáo điều hoặc viết như một AI. Hãy viết tự nhiên như một người Việt Nam bình thường đang bình luận trên Facebook.
    Trả kết quả là 1 đoạn văn bạn viết.
"""

general_comment = gen_summary_comment(client, prompt_config, prompt, models[0], list_news_json)

# Post news to fanpage FaceBook
print("Post news to fanpage FaceBook")
id_page = os.environ["ID_PAGE"]
page_access_token = os.environ["PAGE_ACCESS_TOKEN"]

post_id = post_news_page_facebook(list_news, id_page, page_access_token)
post_comment_facebook(general_comment, post_id, page_access_token)

# Save posted news
print("Save posted news")
save_news(list_news, postedNews_collection)

print("DONE!")