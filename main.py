import pandas as pd
import requests

KEY = ""
PATH_TO_ROUTE = "2021-01-04.csv"
PATH_TO_SAVE = 'save.csv'


def speed_limits(key: str, points: str) -> dict:
    # example points =  38.75807927603043,-9.03741754643809|38.6896537,-9.1770515
    req = f"https://roads.googleapis.com/v1/speedLimits?path={points}&key={key}"
    try:
        response = requests.get(req.format(key)).json()
        snappedPoints = response.get('snappedPoints', 'Error')
        speedLimits = response.get('speedLimits', 'Error')
    except Exception as e:
        return e
    result = {}
    for i, g in zip(snappedPoints, speedLimits):
        result.update({f"{i['location']['latitude']}/{i['location']['longitude']}": {
            'speedLimit': g['speedLimit'],
            'units': g['units']}})
    return result


data = pd.read_csv(PATH_TO_ROUTE)
car_id = list(data.device_id.unique())
result = pd.DataFrame({'id_car': [], 'latitude': [], 'longitude': [], 'speed': []})
for i in car_id:
    coordinate_car = data.query(f"device_id == {i}")
    validation_coordinate = list(
        set([(x, y) for x, y in zip(list(coordinate_car.latitude), list(coordinate_car.longitude))]))[:100]

    request = ""
    print(len(validation_coordinate))
    for tmp in validation_coordinate:
        request += f"{tmp[0]},{tmp[1]}|"
    res = speed_limits(key=KEY, points=request[:-1])

    xs = []
    ys = []
    speeds = []
    for loc, speed in res.items():
        x, y = loc.split('/')
        sp = round(speed['speedLimit'] * 0.621371)  # convert with km/h to miles/h
        xs.append(x)
        ys.append(y)
        speeds.append(sp)

    pd_tmp = pd.DataFrame({'id_car': [str(i)] * len(xs), 'latitude': xs, 'longitude': ys, 'speed': speeds})
    print(pd_tmp.shape)
    result = pd.concat([result, pd_tmp])
result.to_csv(PATH_TO_SAVE, index=False)
