import requests
import wos
import json
import pymysql
import time
from bs4 import BeautifulSoup
from multiprocessing import Process,Queue


link = dict()
manager = multiprocessing.Manager()
citations = manager.dict()
q = Queue()
wosid = input('need to input wos id')
wospwd = input('need to input wos passwrd')
client = wos.WosClient(wosid,wospwd)
pwd = input('sql server pwd need')
connect = pymysql.connect(host='localhost',user='root',password=pwd)
cursor = connect.cursor()
connect.close()


if __name__ == '__main__':
	main()

def main():
	global connect
	global cursor
	connect = pymysql.connect(host='localhost',user='root',password=pwd)
	cursor = connect.cursor()
	cursor.execute('use ta;')
	wconnect()
	jp = Process(target=jsv)
	jp.start()
	mp = Process(target=mains)
	mp.start()
	sp = Process(target=search)
	sp.start()
	
	

def jsv():
	try:
		server = http.server.HTTPServer(('', 20017), jsputter)
		print('Started json server')
		server.serve_forever()
	except KeyboardInterrupt:
		print('break received, shutting down server')
		server.socket.close()

def mains():
	try:
		server = http.server.HTTPServer(('', 20019), handler)
		print('Started http server')
		server.serve_forever()
	except KeyboardInterrupt:
		print('break received, shutting down server')
		server.socket.close()



def search():
	while True:
		cursor.execute('select id from tlist order by time asc limit 500;')
		tal = cursor.fetchall()
		k = 0
		while True:
			if q.empty():
				wosc(tal.pop(0),0)
			else:
				ql = q.get()
				citations[0] = ql
				citations[1] = list()
				citations[2] = list()
				for t in ql:
					wosc(0,t)
					citations[1] += link[t]
					tl = list()
					tn = [ne for ne , ol in link.items() if ol == t ]
					for ti in tn:
						if cursor.exeucte(f'select doi from doi where id ="{ti}";'):
							tl.append(cursor.fetchone()[0])
					citations[1] += tl
					for t1 in link[t]:
						wosc(0,t1)
						citations[2] += link[t1]
					for t1 in tn:
						wosc(t1,0)
						tll = list()
						for ti in [ne for ne , ol in link.items() if ol == t1 ]:
							if cursor.exeucte(f'select doi from doi where id ="{ti}";'):
								tll.append(cursor.fetchone()[0])
						citations[2] += tll						
		f = open(f'result/{int(time.time())}','w')
		for y in link:
			for e in link[y]:
				f.write(y)
				f.write(';')
				f.write(e)
				f.write('\n')
		f.close()
		#--

#20017	json
class jsputter (http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_header()
		self.wfile.write(json.dumps(dict(citations)).encode())
		return None

#20019	main
class handler (http.server.BaseHTTPRequestHandler):
	def do_head(sel):
		sel.send_response(200)
		sel.send_header("Content-type", "text/html")
		sel.end_headers()
	def do_GET(se):
		se.send_response(200)
		se.send_header("Content-type", "text/html")
		se.end_header()
		para = se.path[0:9]
		if para == '/?search=':
			sep = para[9:].replace('\n','')
			sel = sep.split(',')
			while q.empty() == False:
				time.sleep(1)
			q.put(sel)
		else:
			t = int(time.time())
			cursor.execute(f'select count(id) from endlist where time > {t-3600};')
			te = cursor.fetchone()[0]
			cursor.execute(f'select count(id) from endlist;')
			total = cursor.fetchone()[0]
			html = cover(te,total)
			se.wfile.write(html.encode())






def wconnect():
	global client
	client = wos.WosClient(wosid,wospwd)
	io = 1
	il = 1
	while io:
		try:
			client = wos.WosClient(wosid,wospwd)
			client.connect()
			io = 0 
			print('connected')
		except: 
			if il > 5: raise
			else: il += 1
	

def wosc(wid,d):
	global link
	io = 1
	while io:
		if d:
			records = client.search(f'DO={d}').records.split('</REC>')
			for rec in records[:-1]:
				ri = metac(rec)[0]
				cursor.execute(f'insert into doi values("{ri}","{d}");')
				cited = client.citingArticles(ri)
				lin = cited.recordsFound
				ci = 1
				while ci =< lin:
					cn = client.retrieve(cited.queryId,offset=f'{ci}').records.split('</REC>')
					for rec in cn:
						cr = metac(rec)[0]
						if link.get(cr):
							link[cr] += [ri]
						else:
							link[cr] = [ri]
						if cursor.execute(f'select id from endlist where id ="{cr}";'): pass
						else:
							cursor.execute(f'insert into tlist values ("{cr}",{int(time.time())});')	
					ci += 100
				cursor.execute(f'insert into endlist values ("{ri}",{int(time.time())});')
				connect.commit()
			if len(records)>1:
				di(d,ri)
			else:
				di(d,d)
			cursor.execute(f'insert into endlist values ("{d}", {int(time.time())});')
			cursor.execute(f'delete from tlist where id ="{d}";')
			connect.commit()
		elif wid:
			cited = client.citingArticles(wid)
			d = metac(cited.parent)[1]
			if d:
				di(d,wid)
				cursor.execute(f'insert into endlist values ("{d}", {int(time.time())});')
			else:
				cursor.execute(f'insert into blank values ("{wid}",{int(time.time())});')
				connect.commit()
				dio = 0
			ci = 1
			lin = cited.recordsFound
			while  ci =< lin:
				cre = client.retrieve(cited.queryid,offset=f'ci')
				citre = cre.records.split('</REC>')
				for c in citre:
					cid = metac(c)[0]
					if link.get(cid):
						link[cid] += [wid]
					else:
						link[cid] = [wid]				
					if cursor.execute(f'select id from endlist where id = "{cid}";') : pass
					else:
						cursor.execute(f'insert into tlist values ("{cid}",{int(time.time())});')
				connect.commit()
				ci += 1
			cursor.execute(f'insert into endlist values ("{wid}",{int(time.time())});')
			cursor.execute(f'delete from tlist where id ="{wid}";')
			connect.commit()


		


def di(d,ri):
	cref =f'https://api.crossref.org/works/{d}'
	res = requests.get(cref)
	try:
		rej = res.json()
		tt = int(time.time())
		cursor.execute(f'insert into dt values ("{d}",{tt});')
		connect.commit()				
		fj = open(f'raw/{tt}','w')
		fj.write(json.dumps(rej))
		fj.close()
		i = 0
		while True:					
			try:
				rr = rej['message']['reference'][i]['DOI']
				if link.get(ri):
					link[ri] += [rr]
				else:
					link[ri] = [rr]
				if cursor.execute(f'select id from endlist where id = "{rr}";') : pass
				else:
					cursor.execute(f'insert into tlist values ("{rr}",{int(time.time())});')
				i += 1
				connect.commit()
				except:
				if i == 0 :
					cursor.execute(f'insert into blank values ("{d}");')
					connect.commit()
					break
				else: break
	except:
		pass
 





def metac(records):
	try:
		bs = BeautifulSoup(str(records),'xml')
		meta = dict()
		meta['id'] = (bs.UID.string).split(':')[1]	
		try:
			meta['source_journal'] = bs.titles.find('title',type='source').string
		except:
			pass
		try:
			attr = bs.pub_info.attrs
		except:
			pass
		try:
			meta['reference_id'] = f"Volumn {attr['vol']}, Issue {attr['issue']}, {attr['pubyear']}, Pages {bs.pub_info.page.string}"
		except:
			pass
		try:
			meta['year'] = str(attr['pubyear'] )
		except:
			pass
		try:
			meta['source_type'] = str(attr['pubtype'])
		except:
			pass
		try:
			meta['document_type'] = bs.doctype.string
		except:
			pass
		try:
			meta['title'] = bs.titles.find('title',type='item').string.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
		except:
			pass
		try:
			meta['abstract'] = bs.abstract.text.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('\n','')
		except:
			pass
		try:
			kwds = list()
			for kwd in bs.find_all('keyword'):
				if kwd.string.isupper() :
					kwds.append(kwd.string.lower())
				else:
					kwds.append(kwd.string)
			meta['keyword'] = kwds
		except:
			pass
		try:
			meta['issn'] = bs.find('identifier',type='issn').attrs['value']
		except:
			pass
		try:
			meta['eissn'] = bs.find('identifier',type='eissn').attrs['value']
		except:
			pass
		try:
			meta['doi'] = bs.find('identifier',type='doi').attrs['value']
		except:
			pass
		try:
			meta['citedcount'] = bs.citation_related.tc_list.silo_tc.attrs['local_count']
		except:
			pass
		try:
			meta['referencecount'] = bs.refs.attrs['count']
		except:
			pass
		try:
			author_info = dict()
			country = list()
			afl = list()
			afls = dict()
			affs = bs.find_all('address_name')
			for aff in affs:
				affili =list()
				try:
					orgs = aff.find_all('organization')
					coun = aff.country.string
					country.append(coun)					
					for org in orgs:
						orgn = org.string
						affili = [orgn,coun]
						afls[orgn] = affili
				except:
					pass
				try:
					for autho in  aff.find_all('display_name'):
						author_info[autho.string] = affili
				except:
					pass
		except:
			pass
		try:
			meta['author_info'] = author_info
		except:
			pass
		try:
			meta['affiliation'] = list(afls.values())
		except:
			pass
		try:
			meta['author'] = list(author_info.keys())
		except:
			pass
		try:
			meta['country'] = list(set(country))	
		except:
			pass
		#recording section
		f = open(f'raw/{meta["id"]}','w',encoding='utf-8')
		f.write(str(records))
		f.close()
		fm = open(f'metao/{meta["id"]}','w',encoding='utf-8')
		fm.write(json.dumps(meta))
		fm.close()
		return (meta['id'],meta.get('doi'))
	except:
		pass


def html(a,b):
	src = f'''
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title>Trend_Analytics</title>
	</head>
	<body>
		<div>
			<span>
				<p>total		:  {a}</p>
				<p>current		:  {b}</p>
			</span>
		</div>
	</body>
</html>'''
	return src
