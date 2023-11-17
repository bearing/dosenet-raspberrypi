import kromek

# return a dict of members of a class that are POD and not functions, and not
# semi-dundered


def kosher_members(c):
    d = c.__dict__
    variables = filter(
        lambda x: x[0] != "_"
        and (
            isinstance(d[x], int)
            or isinstance(d[x], str)
            or isinstance(d[x], list)
            or isinstance(d[x], float)
        ),
        list(d.keys()),
    )
    return {k: d[k] for k in variables}


def get_value(connection, param="serial", max_attempts=10):
    n = 0
    while True:
        try:
            if param == "serial":
                connection.send(kromek.Message(type=kromek.MessageType.INITIALIZE))
                connection.recv()
                connection.send(kromek.Message(type=kromek.MessageType.GET_SERIAL_NO))

            elif param == "status":
                connection.send(kromek.Message(type=kromek.MessageType.GET_STATUS))

            elif param == "measurement":
                connection.send(kromek.Message(type=kromek.MessageType.GET_16BIT_SPECTRUM))

            elif param == "gain":
                connection.send(kromek.Message(type=kromek.MessageType.GET_GAIN))

            elif param == "bias":
                connection.send(kromek.Message(type=kromek.MessageType.GET_BIAS))

            elif param == "lld-g":
                connection.send(
                    kromek.Message(
                        type=kromek.MessageType.GET_LLD,
                        component=kromek.Component.GAMMA_DETECTOR,
                    )
                )

            elif param == "lld-n":
                connection.send(
                    kromek.Message(
                        type=kromek.MessageType.GET_LLD,
                        component=kromek.Component.NEUTRON_DETECTOR,
                    )
                )

            msg = connection.recv()
            rv = kosher_members(msg)

            if param == "lld-g" or param == "lld-n":
                p4 = param[4]
                rv = {k + "-" + p4: rv[k] for k in rv}

            return rv
        except Exception:
            if n < max_attempts:
                n += 1
            else:
                raise Exception("All get_value retries exhausted")


def set_value(connection, param, value, max_attempts=20):
    n = 0
    value = int(value)
    while True:
        try:
            if param == "gain":
                msg = kromek.Message(type=kromek.MessageType.SET_GAIN)
                msg.gain = value
                connection.send(msg)
                new_value = get_value(connection, param="gain")
                if new_value["gain"] == value:
                    return new_value["gain"]
                else:
                    raise Exception("Failed to set gain")

            elif param == "lld-g":
                msg = kromek.Message(
                    type=kromek.MessageType.SET_LLD,
                    component=kromek.Component.GAMMA_DETECTOR,
                )
                msg.lld = value
                connection.send(msg)
                new_value = get_value(connection, param="lld-g")
                if new_value["lld-g"] == value:
                    return new_value["lld-g"]
                else:
                    raise Exception("Failed to set lld-g")

            elif param == "lld-n":
                msg = kromek.Message(
                    type=kromek.MessageType.SET_LLD,
                    component=kromek.Component.NEUTRON_DETECTOR,
                )
                msg.lld = value
                connection.send(msg)
                new_value = get_value(connection, param="lld-n")
                if new_value["lld-n"] == value:
                    return new_value["lld-n"]
                else:
                    raise Exception("Failed to set lld-n")
        except Exception:
            if n < max_attempts:
                n += 1
            else:
                raise Exception("All set_value retries exahusted'")
