FROM python:3.9.5-alpine as base
RUN apk add --update tzdata

FROM python:3.9.5-alpine
ARG VERSION
ENV USER=
ENV PASSWORD=
ENV BROKER_ADDRESS=
ENV ADDITIONAL_PARAMETERS=
ENV TZ=
ENV MUSL_LOCPATH="/usr/share/i18n/locales/musl"

# Copy zoneinfo
COPY --from=base /usr/share/zoneinfo /usr/share/zoneinfo
# Pillow depenencies
RUN apk --no-cache add --virtual build-dependencies build-base \
    && apk --no-cache add jpeg-dev \
                          zlib-dev \
                          freetype-dev \
                          lcms2-dev \
                          openjpeg-dev \
                          tiff-dev \
                          tk-dev \
                          tcl-dev \
                          musl-locales \
                          musl-locales-lang \
    && pip install weconnect-mqtt==${VERSION} \
    && apk del build-dependencies

CMD weconnect-mqtt --username ${USER} --password ${PASSWORD} --mqttbroker ${BROKER_ADDRESS} ${ADDITIONAL_PARAMETERS}
