import requests
import re
import sys
import time

def login():

	data = {
		'_username': username,
		'_password': password,
		'_remember_me': 'on',
		'login': 'ログイン'
	}

	r1 = s.get('https://piapro.jp/')
	r = s.post('https://piapro.jp/login/exe', data = data, allow_redirects=False)
	
	return s.cookies

def get_info(url):

	r = requests.get(url)

	contentId = re.findall('contentId:\'(.+?)\',', r.text)[0]
	createDate = re.findall('createDate:\'(.+?)\',', r.text)[0]

	return contentId, createDate

def get_mp3(url):

	contentId, createDate = get_info(url)
	htmlURL = f'https://piapro.jp/html5_player_popup/?id={contentId}&cdate={createDate}&p=0'

	r = requests.get(htmlURL)

	title = re.findall("title: '(.+?)'", r.text)
	artist = re.findall("artist: '(.+?)'", r.text)
	mp3 = re.findall("mp3: '(.+?)'", r.text)

	print(title, artist, mp3)

def get_img(url):

	cookies = login()

	r = s.get(url, cookies = cookies)

	html = r.text

	try:
		contentId = re.findall('contentId: \'(.+?)\'', html)[0]
		createDate = re.findall('createDate]" required="required" value="(.+?)"', html)[0]
		license = re.findall('license]" required="required" value="(.+?)"', html)[0]
		folderId = re.findall('defaultFolderId:(.+?),', html)[0]
		token = re.findall('_token]" value="(.+?)"', html)[0]
	except:
		print('作品禁止下载！')
		sys.exit(0)
	
	data = {
	'DownloadWithBookmark[contentId]': contentId,
	'DownloadWithBookmark[createDate]': createDate,
	'DownloadWithBookmark[license]': license,
	'DownloadWithBookmark[folderId]': folderId,
	'DownloadWithBookmark[_token]': token,
	}

	r1 = s.post('https://piapro.jp/download/content_with_bookmark/', data, stream=True)
	Type = r1.headers['Content-Type']
	file_size = r1.headers['Content-Length']

	if Type == 'image/jpeg':
		suffix = '.jpg'
	elif Type == 'image/png':
		suffix = '.png'
	elif Type == 'image/gif':
		suffix = '.gif'

	filename = f"{url.split('/')[-1]}_{createDate}{suffix}"

	with open(filename, 'wb') as f2:
		f2.write(r1.content)
		f2.close()

	print(f'下载完成:{filename}')

def main(url):

	r = requests.get(url)

	category = re.findall('view:\'(.+?)\'', r.text)[0]

	if category == 'audio':
		get_mp3(url)
		sys.exit(0)
	elif category == 'image':
		if username and password:
			get_img(url)
		else:
			print('下载图片需要登录,请填写帐号密码再进行操作。')
			sys.exit(0)
		


if __name__ == '__main__':
	s = requests.session()
	username = '' # 帐号
	password = '' # 密码
	url = sys.argv[1]
	start = time.time()
	main(url)
	end = time.time()
	print('用时:{}秒'.format(int(end - start)))
