from markdownify import markdownify as md
# from ezmysql import ConnectionSync

# db=ConnectionSync(host='124.223.224.49', database='blog', user='root', password='1486922887')
# result=db.query('select id, body from post')
# for i in result:
#     body=md(i['body'])
#     db.table_update('post',{'body':body},'id',i['id'])

print(md('''
<p>Hello world!</p>

<p>It&#39;s Lingfeng Huang from Hangzhou, Zhejiang,&nbsp;People&#39;s Republic of China.</p>

<p>Born on May 8th 2001.</p>

<p>I like computer&nbsp;games, photography, computer programming&nbsp;and body-building.</p>

<p>I also want to make friends with people around the world who are kind and willing to exchange ideas.</p>

<p>This is my email:&nbsp;hlf01@icloud.com.</p>

<p>You can also find me with my Links.</p>

<p>Talking in Messenger or Telegram is also welcome~</p>'''))