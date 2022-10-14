metadata {
	definition (name: "Virtual iStart Device", namespace: "TSTD.ISV", author: "Julia Beiferman") {
		capability	"Actuator"
		command 	"on"
		command 	"off"
		command		"restart"
	}
	preferences {
		input name: "txtEnable", type: "bool", title: "Enable descriptionText logging", defaultValue: true
	}
}

def installed() {
	log.warn "installed..."
	off()
}

def updated() {
	log.warn "updated..."
	log.warn "description logging is: ${txtEnable == true}"
}

def parse(String description) {
}

def on() {
	def descriptionText = "${device.displayName} was turned on"
	if (txtEnable) log.info "${descriptionText}"
	sendEvent(name: "switchPosition", value: "on", descriptionText: descriptionText)
}

def off() {
	def descriptionText = "${device.displayName} was turned off"
	if (txtEnable) log.info "${descriptionText}"
	sendEvent(name: "switchPosition", value: "off", descriptionText: descriptionText)
}

def restart() {
	def descriptionText = "${device.displayName} was restarted"
	if (txtEnable) log.info "${descriptionText}"
	sendEvent(name: "switchPosition", value: "restart", descriptionText: descriptionText)
}
