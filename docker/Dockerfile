FROM python:3.9.5-alpine

ENV USER=
ENV PASSWORD=
ENV BROKER_ADDRESS=
ENV ADDITIONAL_PARAMETERS=

# Pillow depenencies
RUN apk --no-cache add  jpeg-dev \
                        zlib-dev \
                        freetype-dev \
                        lcms2-dev \
                        openjpeg-dev \
                        tiff-dev \
                        tk-dev \
                        tcl-dev

RUN pip install weconnect-mqtt

CMD weconnect-mqtt --username ${USER} --password ${PASSWORD} --mqttbroker ${BROKER_ADDRESS} ${ADDITIONAL_PARAMETERS}
