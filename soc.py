import requests
from fuzzywuzzy import fuzz

class Soc:
	def __init__(self, campus="NB", semester="12015", level="U,G"):
		self.base_url = "http://sis.rutgers.edu/soc"
		self.params = {"semester": semester, "campus": campus, "level": level}
		self.headers = {
			"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"
		}

	def get_subjects(self):
		# http://sis.rutgers.edu/soc/subjects.json?semester=12015&campus=NB&level=U
		subjects_url = "/subjects.json"
		r = requests.get(self.base_url + subjects_url, params=self.params, 
						headers=self.headers)

		if r.status_code != requests.codes.ok:
			return []

		subjects = []
		for sub in r.json():
			if "description" not in sub or "code" not in sub:
				continue
			subjects.append({"description": sub["description"], 
						     "code": sub["code"]})	
		return subjects

	def find_prof(self, name, department):
		name = name.lower()
		course_url = "/courses.json"
		params = self.params.copy()
		params.update({"subject": department})
		
		r = requests.get(self.base_url + course_url, params=params, 
						headers=self.headers)

		if r.status_code != requests.codes.ok:
			print "Error"
			return []

		prof_locs = []
		for listing in r.json():
			found_prof = False
			prof_listing = {}

			if "sections" not in listing:
				continue

			meet_times = []
			for section in listing["sections"]:
				if "instructors" not in section or not section["instructors"]:
					continue
				prof_name = self._search_prof(name, section["instructors"])
				if not prof_name:
					continue
				prof_listing["name"] = prof_name
				if "meetingTimes" not in section or not section["meetingTimes"]:
					continue
				meeting_times = self._get_meeting_time_info(section["meetingTimes"])
				for m in meeting_times:
					meet_times.append(m)
				found_prof = True

			prof_listing["meeting_times"] = meet_times
			prof_listing["course"] = "-"
			if "title" in listing:
				prof_listing["course"] = listing["title"]

			if found_prof:
				prof_locs.append(prof_listing)

		return prof_locs


				
	def _search_prof(self, name, instructors):
		for instructor in instructors:
			if "name" not in instructor or len(instructor["name"]) == 1:
				continue;
			inst_name = instructor["name"].lower()
			if inst_name == name or fuzz.partial_ratio(inst_name, name) > 90:
				#print "%s [%s], %s" % (instructor["name"], fuzz.partial_ratio(instructor["name"], name), name)
				return instructor["name"]
		return None

	def _get_meeting_time_info(self, meet_times):
		sections = []
		for meet_time in meet_times:
			# omit recitation sections
			if "meetingModeDesc" in meet_time and meet_time["meetingModeDesc"] != "LEC":
				continue

			if "startTime" not in meet_time or not meet_time["startTime"]:
				continue;
			start_time = meet_time["startTime"]

			if "endTime" not in meet_time or not meet_time["endTime"]:
				continue
			end_time = meet_time["endTime"]

			if "pmCode" not in meet_time or not meet_time["pmCode"]:
				continue
			pm_code = meet_time["pmCode"]
			if pm_code == "P":
				pm_code = "PM"
			else:
				pm_code = "AM"

			if "meetingDay" not in meet_time or not meet_time["meetingDay"]:
				continue
			meeting_day = self._get_day(meet_time["meetingDay"])


			if "buildingCode" not in meet_time or not meet_time["buildingCode"]:
				continue
			building_code = meet_time["buildingCode"]

			if "roomNumber" not in meet_time or not meet_time["roomNumber"]:
				continue
			room_number = meet_time["roomNumber"]

			entry = "%s%s-%s%s %s %s-%s" % (start_time, pm_code, end_time, 
							pm_code, meeting_day, building_code, room_number)

			if "campusName" in meet_time and meet_time["campusName"]:
				entry += " [%s]" % meet_time["campusName"]

			sections.append(entry)
		return sections

	def _get_day(self, day_code):
		if day_code == "M":
			return "Monday"
		elif day_code == "T":
			return "Tuesday"
		elif day_code == "W":
			return "Wednesday"
		elif day_code == "TH":
			return "Thursday"
		elif day_code == "F":
			return "Friday"
		else:
			return "Day not recognized"


#soc = Soc()
#print soc.find_prof("venug", 198);
