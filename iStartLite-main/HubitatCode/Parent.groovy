/*
 *	iStart (Parent)
 *
 *  1.0.0 First Release
 * 
 * 
 */

def setVersion(){
	state.version = "1.0.0" // Version number of this app
	state.InternalName = "iStart3Parent"   // this is the name used in the JSON file for this app
}

definition(
    name: "iStart3 Parent",
    namespace: "TSTD.ISV",
    singleInstance: true,
    author: "Craig Romei",
    description: "Control a bunch of iStarts. - Parent",
    category: "Restart",
    iconUrl: "",
    iconX2Url: "",
    iconX3Url: "",
    importUrl: "https://raw.githubusercontent.com/napalmcsr/Hubitat_Napalmcsr/master/Apps/BathroomHumidityFan/BathroomHumidity.src")

preferences {
	page(name: "mainPage")
}

def mainPage() {
	return dynamicPage(name: "mainPage", title: "", install: true, uninstall: true) {
        if(!state.Installed) {
            section("Hit Done to install iStart App") {
        	}
        }
        else {
        	section("<b>Create a new iStart Instance.</b>") {
            	app(name: "childApps", appName: "iStart3 Child", namespace: "TSTD.ISV", title: "New iStart Instance", multiple: true)
        	}
    	}
    }
}

def installed() {initialize()}
def updated() {initialize()}
def initialize() {
    
    if(!state.Installed) 
    {
        state.Installed = true
   	}
    
    unsubscribe()
    log.info "Initialised with settings: ${settings}"
    log.info "There are ${childApps.size()} installed child apps"
    childApps.each {child ->
    log.info "Child app: ${child.label}"
    }    
}
	 


def debuglog(statement)
{   
               def logL = 0
    if (logLevel) logL = logLevel.toInteger()
    if (logL == 0) {return}//bail
    else if (logL >= 2)
               {
                              log.debug(statement)
               }
}
def infolog(statement)
{       
               def logL = 0
    if (logLevel) logL = logLevel.toInteger()
    if (logL == 0) {return}//bail
    else if (logL >= 1)
               {
                              log.info(statement)
    }
}
def getLogLevels(){
    return [["0":"None"],["1":"Running"],["2":"NeedHelp"]]
}


