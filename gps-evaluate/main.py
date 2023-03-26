import plotly.graph_objects as go


mapbox_access_token = open("./mapbox_token").read()
lat_tst = '55.728485'
lon_tst ='37.610004'

def read_port():
	pass

def show_map(valid_lat_group, valid_lon_group, invalid_lat_group, invalid_lon_group):
	fig = go.Figure()

	fig.add_trace(go.Scattermapbox(
	lat=invalid_lat_group,
    lon=invalid_lon_group,
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=14,
		color='rgb(207, 52, 118)'
    	),
	    text=['WRONG MISIS'] * len(invalid_lon_group),
    ))

	fig.add_trace(go.Scattermapbox(
	lat=valid_lat_group,
    lon=valid_lon_group,
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=14,
		color='rgb(113, 188, 120)'
    	),
	    text=['VALID MISIS'] * len(valid_lon_group),
    ))

	fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=int(lat_tst),
            lon=int(lon_tst)
        ),
        pitch=0,
        zoom=5
    	)
	)

	fig.show()

def convert_to_decimal_degrees(lat, geopart_lat, lon, geopart_lon):
	lattitude = 0.0
	longitude = 0.0
	direction = {'N':1.0, 'S':-1.0, 'E': 1.0, 'W':-1.0}
	
	lattitude = float("{0:.6f}".format((int(lat[:2]) + float(lat[2:]) / 60) * direction[geopart_lat]))
	longitude = float("{0:.6f}".format((int(lon[:2]) + float(lon[2:]) / 60) * direction[geopart_lon]))

	return lattitude, longitude

def process_data(path):
	log_data = []

	with open(path, "r") as file:
		log = file.readlines()
		for row in range(0, len(log)):
			current_data = log[row].split(',')
			if current_data[0] != '$GPRMC' and current_data[0] != '$GPGGA':
				continue
			if current_data[0] == '$GPRMC' and current_data[2] != 'A':
				row += 9
				continue
			if current_data[0] == '$GPGGA':
				lattitude,longitude = convert_to_decimal_degrees(current_data[2], current_data[3], current_data[4][1:], current_data[5])
				log_data.append({
					'time': float(current_data[1]),
					'lat': lattitude,
					'lon': longitude,
					'sat_num': int(current_data[7]),
					'hdop': float(current_data[8])
					})
	return log_data

def evaluate_gpsdata(gps_data):
	green_signals = []
	red_signals = []
	prev_signal = None

	for signal in gps_data:
		signal['flag'] = True
		current_flag = True
		if 'lat' not in signal.keys() or 'lon' not in signal.keys() or 'time' not in signal.keys() or 'sat_num' not in signal.keys() or 'hdop' not in signal.keys():
			current_flag = False
			signal['flag'] = False
			# continue

		if int(signal['sat_num']) < 4:
			current_flag = False
			signal['flag'] = False
			# continue

		if float(signal['hdop']) > 2.0:
			current_flag = False
			signal['flag'] = False
			# continue

		if prev_signal:
			del_lat = signal['lat'] - float(lat_tst)
			del_lon = signal['lon'] - float(lon_tst)
			del_time = signal['time'] - 121426
			if abs(del_lat/del_time) > (360.0/24.0)/3600.0/9600.0 or abs(del_lon/del_time) > (360.0/24.0)/3600.0/9600.0:
				current_flag = False
				signal['flag'] = False
				# continue

		if signal['flag'] == True:
			green_signals.append(signal)
			prev_signal = signal
		else:
			red_signals.append(signal)

	return green_signals, red_signals

def read_log(path):
	gps_data = process_data(path)
	valid_gps, invalid_gps = evaluate_gpsdata(gps_data)

	valid_lat_group = []
	valid_lon_group = []
	invalid_lat_group = []
	invalid_lon_group = []

	for signal in valid_gps:
		valid_lat_group.append(signal['lat'])
		valid_lon_group.append(signal['lon'])

	for signal in invalid_gps:
		invalid_lat_group.append(signal['lat'])
		invalid_lon_group.append(signal['lon'])

	show_map(valid_lat_group, valid_lon_group, invalid_lat_group, invalid_lon_group)

if __name__ == '__main__':
	read_log('log.txt')