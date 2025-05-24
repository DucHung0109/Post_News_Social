**FLOW:** Run at 11:30 PM everyday, read new article of day and post Facebook
- Take top headlines article by API of NewsAPI.
- Delete articles saved more than 6 days.
- Take posted articles, saved on MongoDB.
- Take some articles about hot topic(netizens interested in).
- Filter article by Gemini, take articles which have distinct difference with posted articles.
- Generate description, comment, title in VietNamese, content in VietNamese by Gemini.
- Generate general comments for all chosen articles in day.
- Use Meta API to posted articles on FanPage FaceBook.
- Save new articles on MongoDB.

**FLOW 2:** Run at 7:00 AM everyday, read article of yesterday, which was saved on MongoDB after posted Facebook
- Take articles from MongoDB
- Read token to post Threads from MongoDB
- Post article by Meta API