FROM azul/zulu-openjdk:13

WORKDIR /opt/Lavalink

COPY Lavalink.jar Lavalink.jar
COPY application.yml application.yml

EXPOSE 2333

# CMD ["java", "-jar", "Lavalink.jar"]
ENTRYPOINT ["java", "-Djdk.tls.client.protocols=TLSv1.1,TLSv1.2", "-Xmx4G", "-jar", "Lavalink.jar"]