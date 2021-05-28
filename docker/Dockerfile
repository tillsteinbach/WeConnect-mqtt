FROM python:3.9.5-alpine

ENV USER=
ENV PASSWORD=
ENV BROKER_ADDRESS=
ENV ADDITIONAL_PARAMETERS=

RUN pip install weconnect-mqtt

CMD weconnect-mqtt --username ${USER} --password ${PASSWORD} --mqttbroker ${BROKER_ADDRESS} ${ADDITIONAL_PARAMETERS}
