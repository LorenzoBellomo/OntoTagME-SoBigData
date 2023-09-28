FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive \
  JAVA_VERSION=jdk-11.0.10+9

COPY ./Volume/config.sample.xml /opt/config.sample.xml
COPY ./Volume/WikipediaAnchorParser.java /opt/WikipediaAnchorParser.java
COPY ./Volume/wikipatterns.properties /opt/wikipatterns.properties
COPY ./Volume/init.sh .
ADD ./Volume/multi-tagme-master_final /opt/multi-tagme-master_final
RUN chmod +x init.sh

# programs installation
RUN \
  apt-get update && \
  #apt-get install -y software-properties-common && \
  #add-apt-repository ppa:deadsnakes/ppa && \
  apt-get install -y \
  tzdata \
  nano \
  unzip \
  curl \
  wget \
  ca-certificates \
  fontconfig \
  locales \
  #python3.8 \
  python3 \
  ant \
  git-all \
  python3-pip && \
  pip3 install gdown && \
  pip3 install xmltodict &&  \
  pip3 install unidecode &&  \
  pip3 install nltk && \
  pip3 install flask && \
  pip3 install bioc && \
  pip3 install lxml


# install openjdk 11
RUN set -eux; \
  ARCH="$(dpkg --print-architecture)"; \
  case "${ARCH}" in \
  aarch64|arm64) \
  ESUM='420c5d1e5dc66b2ed7dedd30a7bdf94bfaed10d5e1b07dc579722bf60a8114a9'; \
  BINARY_URL='https://github.com/AdoptOpenJDK/openjdk11-binaries/releases/download/jdk-11.0.10%2B9/OpenJDK11U-jdk_aarch64_linux_hotspot_11.0.10_9.tar.gz'; \
  ;; \
  armhf|armv7l) \
  ESUM='34908da9c200f5ef71b8766398b79fd166f8be44d87f97510667698b456c8d44'; \
  BINARY_URL='https://github.com/AdoptOpenJDK/openjdk11-binaries/releases/download/jdk-11.0.10%2B9/OpenJDK11U-jdk_arm_linux_hotspot_11.0.10_9.tar.gz'; \
  ;; \
  ppc64el|ppc64le) \
  ESUM='e1d130a284f0881893711f17df83198d320c16f807de823c788407af019b356b'; \
  BINARY_URL='https://github.com/AdoptOpenJDK/openjdk11-binaries/releases/download/jdk-11.0.10%2B9/OpenJDK11U-jdk_ppc64le_linux_hotspot_11.0.10_9.tar.gz'; \
  ;; \
  s390x) \
  ESUM='b55e5d774bcec96b7e6ffc8178a17914ab151414f7048abab3afe3c2febb9a20'; \
  BINARY_URL='https://github.com/AdoptOpenJDK/openjdk11-binaries/releases/download/jdk-11.0.10%2B9/OpenJDK11U-jdk_s390x_linux_hotspot_11.0.10_9.tar.gz'; \
  ;; \
  amd64|x86_64) \
  ESUM='ae78aa45f84642545c01e8ef786dfd700d2226f8b12881c844d6a1f71789cb99'; \
  BINARY_URL='https://github.com/AdoptOpenJDK/openjdk11-binaries/releases/download/jdk-11.0.10%2B9/OpenJDK11U-jdk_x64_linux_hotspot_11.0.10_9.tar.gz'; \
  ;; \
  *) \
  echo "Unsupported arch: ${ARCH}"; \
  exit 1; \
  ;; \
  esac; \
  curl -LfsSo /tmp/openjdk.tar.gz ${BINARY_URL}; \
  echo "${ESUM} */tmp/openjdk.tar.gz" | sha256sum -c -; \
  mkdir -p /opt/java/openjdk; \
  cd /opt/java/openjdk; \
  tar -xf /tmp/openjdk.tar.gz --strip-components=1; \
  rm -rf /tmp/openjdk.tar.gz;

ENV JAVA_HOME=/opt/java/openjdk \
    PATH="/opt/java/openjdk/bin:$PATH"


# gradle installation
RUN mkdir /opt/gradle && \
  cd /opt/gradle && \
  wget https://services.gradle.org/distributions/gradle-6.8.3-bin.zip && \
  unzip gradle-*.zip && \
  cd / && \
  echo export GRADLE_HOME=/opt/gradle/gradle-6.8.3 >> /etc/profile.d/gradle.sh && \
  echo export PATH=${GRADLE_HOME}/bin:${PATH} >> /etc/profile.d/gradle.sh

ENV GRADLE_HOME=/opt/gradle/gradle-6.8.3 \
    PATH="/opt/gradle/gradle-6.8.3/bin:$PATH"

# download TAGME from GIT
RUN echo "TAGME downloading...." && \
  cd /opt && \
  git clone https://github.com/gammaliu/tagme/
  
# configure TopicalTagME db
CMD ["bin/bash", "./init.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]