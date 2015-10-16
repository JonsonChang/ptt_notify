# ptt_notify
設定PTT 追綜特定關鍵字，並發送email 通知。

# 如何使用
python 2.7以上

在config.json 中設定好相關的版面，和關鍵字，還有要寄出通知的Email。

執行 **python main.py** 就會開始監看相關的版面，只有要新的文章內容符合你所設定的關鍵字，就會寄出email 通知。(程式執行前的文章，並不會去重新找一遍)


# config.json
每一個版可以設定不同的關鍵字，通知的Email 可以同時使用多組。


		{
			"setting":[
			  {
				 "board":"wanted",
				 "keywords":[
					"徵求",
					"早安",
					"晚安"
				 ]
			  },
			  {
				 "board":"Gossiping",
				 "keywords":[
					"爆",
					"柯文哲",
					"問掛"
				 ]
			  }
		   ],
		   "mail":"puperchang@gmail.com"
		}



