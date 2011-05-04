SRC_DIR = src
DIST_DIR = dist

MINIFIER = yuicompressor
MINIFIER_JAR = ~/dev/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar

JD_VER = $(shell cat version.txt)
JD_JS = ${DIST_DIR}/jsondiff-${JD_VER}.js
JD_PY = ${DIST_DIR}/jsondiff-${JD_VER}.py

all: ${DIST_DIR} ${JD_PY} ${JD_JS} min
	@@echo "Done."

${DIST_DIR}:
	@@mkdir -p ${DIST_DIR}

${JD_PY}: ${SRC_DIR}/jsondiff.py
	@@cp ${SRC_DIR}/jsondiff.py ${JD_PY}

${JD_JS}: ${SRC_DIR}/jsondiff.coffee
	@@coffee -c ${SRC_DIR}/jsondiff.coffee
	@@cp ${SRC_DIR}/jsondiff.js ${JD_JS}

min: ${JD_JS}
	@@if type -P ${MINIFIER} &>/dev/null; then \
		${MINIFIER} -o ${DIST_DIR}/jsondiff-${JD_VER}-min.js ${JD_JS}; \
	elif type -P java &>/dev/null && [ -f ${MINIFIER_JAR} ]; then \
		java -jar ${MINIFIER_JAR} -o ${DIST_DIR}/jsondiff-${JD_VER}-min.js ${JD_JS}; \
	else \
		@@echo "Install ${MINIFIER}"; \
	fi
	

clean:
	@@echo "Removing directory:" ${DIST_DIR}
	@@rm -rf ${DIST_DIR}
