import cgi
import datetime
import urllib
import webapp2

import random
import jinja2
import os
import csv
from webapp2_extras import sessions
import json

import middleware as mw

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class MainPage(BaseHandler):
    def get(self):
        login_in = self.session.get('login_in')

        if not login_in:
        	self.redirect('/euler')

        template = jinja_environment.get_template('mainCal.html')
        self.response.out.write(template.render())

class HelpPage(BaseHandler):
    def get(self):
        
        template = jinja_environment.get_template('help.html')
        self.response.out.write(template.render())


class HomeHandler(BaseHandler):
    def get(self):
    	login_in = self.session.get('login_in')
    	login_in = None
    	if login_in:
    		self.redirect('/')

        q = self.request.get('q').strip().lower()

        if q == '':
        	euler_id = None
        else:
        	euler_id = self.session.get('euler_id')
        
        error_msg = False
        euler_dict = {1:('e','euler_e.jpg',30,-240,100,64,70),
        				2:('=','euler_equal.jpg',30,110,100,64,70),
        				3:('i','euler_i.jpg',25,-185,50,22,45),
        				4:('1','euler_one.jpg',30,30,100,64,70),
        				5:('+','euler_plus.jpg',30,-65,100,64,70),
        				6:('0','euler_zero.jpg',30,200,100,64,70)
        			}

        if not euler_id:
            euler_id = random.randint(1,6)
            self.session['euler_id'] = euler_id
        else:
        	correct_ans = False
        	if euler_dict[euler_id][0] == q:
        		correct_ans = True

        	if correct_ans:
        		self.session['login_in'] = True
        		self.redirect('/')
        	else:
        		error_msg = True

        template_values = {
            'error_msg': error_msg,
            'euler_pic': '/images/'+euler_dict[euler_id][1],
            'q':q,
            'top':euler_dict[euler_id][2],
            'left':euler_dict[euler_id][3],
            'height':euler_dict[euler_id][4],
            'width':euler_dict[euler_id][5],
            'size':euler_dict[euler_id][6]
        }

        template = jinja_environment.get_template('euler.html')
        self.response.out.write(template.render(template_values))

class listEvents(BaseHandler):
	def get(self):
		evts = mw.listAllEvents()

		forJS = []

		for evt in evts['items']:
			forJS.append({'id':evt['id'],
				'title':evt['summary'],
				'start':evt['start']['dateTime'],
				'end':evt['end']['dateTime'],
				'allDay':False,
				'description':evt['description'] if evt.has_key('description') else '',
				'backgroundColor':'#640125' if evt.has_key('description') else '#3a87ab'
				})

		return self.response.out.write(json.dumps(forJS))

class listStudent(BaseHandler):
	def get(self):
		q = self.request.get('q').lower()

		forJS = []

		for stu in student_list:
			if (stu[1].lower().find(q) != -1):
				forJS.append(stu[1]+'|'+str(stu[0]))
		self.response.out.write('\n'.join(forJS))

class updateEvent(BaseHandler):
	def post(self):
		evt_id = self.request.get('evt_id')
		uid = self.request.get('data')
		act_type = self.request.get('act_type')

		ulist = uid.split(',')
		su_list = []
		mail_list = []
		for x in ulist:
			if x != '':
				su_list.append(student_list[int(x)][1])
				mail_list.append(student_list[int(x)][3])

		if act_type=='reserve':
			self.response.out.write(mw.updateEvent(evt_id, ' AND '.join(su_list), mail_list))
		else:
			self.response.out.write(mw.cancelEvent(evt_id, su_list, mail_list))
		

def cacheStudent():
	t = csv.reader(open('r.csv','rb'))
	t.next()
	l = []
	i = 0
	for x in t:
		if x[3].lower()=='student':
			l.append([i]+x)
			i = i + 1
	return l

student_list = cacheStudent()

config={}
config['webapp2_extras.sessions'] = {'secret_key':'MFE230QPrivateTutoring'}

app = webapp2.WSGIApplication([('/', MainPage), 
								('/euler', HomeHandler),
								('/list-events', listEvents),
								('/list-students', listStudent),
								('/help',HelpPage),
								('/update_evt', updateEvent)],
                              debug=True, config=config)