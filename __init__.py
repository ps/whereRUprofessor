import logging
from datetime import date
from flask import Flask,render_template,request,jsonify
from logging.handlers import RotatingFileHandler
from soc import Soc

app=Flask(__name__)

@app.route('/')
def main_page():
	# fetch passed parameters
	#query=request.args.get("query")
	#lang=request.args.get("lang")

	soc = Soc()
	departments = soc.get_subjects()

	return render_template('index.html', departments=departments,
										 year=date.today().year)

@app.route('/find/<int:dep_code>/<prof_name>')
@app.route('/find/<int:dep_code>/<prof_name>/<int:grad_under>')
def find_page(dep_code, prof_name, grad_under=None):
	soc = None
	if grad_under == 1:
		soc = Soc(level="U")
	elif grad_under == 2:
		soc = Soc(level="G")
	else:
		soc = Soc()

	prof_list = soc.find_prof(prof_name, dep_code)
	return jsonify(info=prof_list)

if __name__ == "__main__":
	# file_handler = RotatingFileHandler('../wiki_error.log', 
 #                maxBytes=1024 * 1024 * 100, backupCount=20)
	# file_handler.setLevel(logging.INFO)
	# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	# file_handler.setFormatter(formatter)
	# app.logger.addHandler(file_handler)
	app.debug = True
	app.run()

