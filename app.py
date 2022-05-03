from flask import Flask ,redirect,render_template , request ,jsonify
import pymysql
from dbutils.pooled_db import PooledDB
import os
from boto3.session import Session
import boto3
from dotenv import load_dotenv
load_dotenv()
app=Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/post_content", methods=["Post"])
def post_content():
	text_content = request.values['text_content']
	image_data  = request.files['image_data']
	aws_key =  os.environ.get('aws_access_key_id')# 【你的 aws_access_key】
	aws_secret = os.environ.get('aws_secret_access_key') # 【你的 aws_secret_key】
	session = Session(aws_access_key_id=aws_key,
	aws_secret_access_key=aws_secret,
	region_name="us-east-1") # 此處根據自己的 s3 地區位置改變
	s3 = session.resource("s3")
	client = session.client("s3")
	bucket = "levle3-test-data" # 【你 bucket 的名字】 # 首先需要保證 s3 上已經存在該儲存桶，否則報錯
	upload_data = image_data
	upload_key = image_data.filename
	file_obj = s3.Bucket(bucket).put_object(Key=upload_key, Body=upload_data)

	connection = link_mysql()
	cursor = connection.cursor()
	cursor.execute( "INSERT INTO level3_s3 (text_data,image_data) VALUES (%s,%s)" , (text_content ,upload_key) )
	connection.commit()
	cursor.close()

	return redirect("/")

@app.route("/alldata")
def alldata():
	connection = link_mysql()
	cursor = connection.cursor()
	sql = "select COUNT(id) from level3_s3"
	cursor.execute(sql)
	connection.commit()
	id_count = cursor.fetchall()
	return jsonify({'data':id_count}),200

@app.route("/show_text/<id>")
def show_text(id):
	connection = link_mysql()
	cursor = connection.cursor()
	sql = " select * from level3_s3  limit {} ,1".format(id)
	cursor.execute(sql)
	connection.commit()
	id_data = cursor.fetchone()
	cursor.close()
	return jsonify({'data':id_data[1]}) ,200 

@app.route("/show_image/<id>")
def show_image(id):
	connection = link_mysql()
	cursor = connection.cursor()
	sql = " select * from level3_s3  limit {} ,1".format(id)
	cursor.execute(sql)
	connection.commit()
	id_data = cursor.fetchone()
	connection.commit()
	cursor.close()
	# resp = make_response(id_data[2])
	# resp.headers['Content-Type'] = 'image/png'
	s3_clinent = boto3.client(
		's3',
		aws_access_key_id = os.environ.get('aws_access_key_id'),# 【你的 aws_access_key】
		aws_secret_access_key = os.environ.get('aws_secret_access_key'), # 【你的 aws_secret_key】
	)

	response = s3_clinent.get_object(Bucket='levle3-test-data',Key=id_data[2])
	data=response['Body'].read()
	return data

def link_mysql():
	try:
		POOL = PooledDB(
		creator=pymysql,  # 使用連結資料庫的模組
		maxconnections=6,  # 連線池允許的最大連線數，0和None表示不限制連線數
		mincached=2,  # 初始化時，連結池中至少建立的空閒的連結，0表示不建立
		maxcached=5,  # 連結池中最多閒置的連結，0和None不限制
		maxshared=3,  # 連結池中最多共享的連結數量，0和None表示全部共享。PS: 無用，因為pymysql和MySQLdb等模組的 threadsafety都為1，所有值無論設定為多少，_maxcached永遠為0，所以永遠是所有連結都共享。
		blocking=True,  # 連線池中如果沒有可用連線後，是否阻塞等待。True，等待；False，不等待然後報錯
		maxusage=None,  # 一個連結最多被重複使用的次數，None表示無限制
		setsession=[],  # 開始會話前執行的命令列表。如：["set datestyle to ...", "set time zone ..."]
		ping=0,
		# ping MySQL服務端，檢查是否服務可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
		host=os.environ.get('aws_rds_host'),
		port=3306,
		user=os.environ.get('aws_rds_user'),
		password=os.environ.get('aws_rds_password'),
		database=os.environ.get('database'),
		charset='utf8'
	)
		conn = POOL.connection()
		
		return conn
	except:
		msg = "伺服器內部錯誤"
		data = {
		"error":True,
		"message":msg
		}

		return jsonify({'data':data}) ,500 
	
		

app.run(host='0.0.0.0',port=3000)