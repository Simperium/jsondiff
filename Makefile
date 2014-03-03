SRC_DIR = src
DIST_DIR = dist

MINIFIER = yuicompressor
MINIFIER_JAR = ~/dev/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar

JD_VER = $(shell cat version.txt)
JD_JS = ${DIST_DIR}/jsondiff-${JD_VER}.js
JD_MIN_JS = ${DIST_DIR}/jsondiff-${JD_VER}.min.js
JD_SRC = ${SRC_DIR}/jsondiff.coffee
JD_SRC_JS = $(JD_SRC:%.coffee=%.js)

all: ${DIST_DIR} ${JD_JS} ${JD_MIN_JS}
	@@echo "Done."

${DIST_DIR}:
	@@mkdir -p ${DIST_DIR}

${JD_JS}: ${JD_SRC_JS}
	cp ${JD_SRC_JS} ${JD_JS}

${JD_SRC_JS}: ${JD_SRC}
	coffee -c $<

${JD_MIN_JS}: ${JD_JS}
	@@if type -P ${MINIFIER} &>/dev/null; then \
		${MINIFIER} -o ${JD_MIN_JS} ${JD_JS}; \
	elif type -P java &>/dev/null && [ -f ${MINIFIER_JAR} ]; then \
		java -jar ${MINIFIER_JAR} -o ${JD_MIN_JS} ${JD_JS}; \
	else \
		@@echo "Install ${MINIFIER}"; \
	fi
	

clean:
	rm -rf ${JD_SRC_JS}
	rm -rf ${JD_JS}
	rm -rf ${JD_MIN_JS}
