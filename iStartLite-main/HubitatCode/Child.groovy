import groovy.json.*

def setVersion()
{
	state.version = "1.0.0" // Version number of this app
	state.InternalName = "iStart3Child"   // this is the name used in the JSON file for this app
	}
definition(
    name: "iStart3 Child",
    namespace: "TSTD.ISV",
    author: "Craig Romei",
    description: "Control an iStart relay box",
    category: "Restart",
    parent: "TSTD.ISV:iStart3 Parent",
    iconUrl: "https://raw.githubusercontent.com/napalmcsr/SmartThingsStuff/master/smartapps/craig-romei/poolpump.jpg",
    iconX2Url: "https://raw.githubusercontent.com/napalmcsr/SmartThingsStuff/master/smartapps/craig-romei/poolpump.jpg",
    iconX3Url: "https://raw.githubusercontent.com/napalmcsr/SmartThingsStuff/master/smartapps/craig-romei/poolpump.jpg"
)
preferences {
    page(name: "pageConfig") // Doing it this way elimiates the default app name/mode options.
}
def pageConfig()
{
	dynamicPage(name: "", title: "", install: true, uninstall: true, refreshInterval:0) {
    
		section("Title") 
        {
			section() {label title: "Enter a name for this automation", name: "testerName", required: true}

		}
        		
    	section("iStart Relay Box")
        {
  
		    input "RunRelay", "capability.switch", title: "Run:", required: true
		    input "StartRelay", "capability.switch", title: "Start:", required: true

        }
                
	    section("Logging")
	    {                       
		    input "logLevel","enum",title: "IDE logging level",required: true,options: getLogLevels(),defaultValue : "2"
	    }
	}
}
def installed()
{
    initialize()
}
def uninstalled()
{
    deleteChildDevice("iStart_${app.id}")
}
def updated()
{
	unsubscribe()
    initialize()
}



def initialize()
{
    debuglog "initializing iStart"
    def deviceWrapper = getChildDevice("iStart_${app.id}")
    
    if(!deviceWrapper) {
        // Create the virtual Button For App
        
	    Map RestartSwitchProperties = [:]
        RestartSwitchProperties.isComponent = true
        RestartSwitchProperties.label  = app.getLabel()
        RestartSwitchProperties.name  = "iStart Virtual Switch"
        deviceWrapper = addChildDevice("TSTD.ISV", "Virtual iStart Device", "iStart_${app.id}", RestartSwitchProperties)
    }
    
    
    subscribe(deviceWrapper, "switchPosition", SwitchHandler)
    infolog "Initialize complete"
}

def SwitchHandler(evt){
    debuglog "Switch event ${evt.value}"
    
    if (evt.value == "on") {
        OnHandler()
    } else if (evt.value == "off"){
        OffHandler()
    } else if (evt.value == "restart"){
        RestartHandler()
    }
        
}



def Run()
{
    RunRelay.off()
    StartRelay.off()

}

def Start()
{
    RunRelay.off()
    StartRelay.on()

}

def Off()
{
    RunRelay.on()
    StartRelay.off()

}

def OffHandler()
{
    RunRelay.on()
    StartRelay.off()

}

def OnHandler()
{
    Run()
    pause(500)
    Start()
    pause(10000)
    Run()   
}

def RestartHandler()
{
    Off() // off 5 seconds
    pause(5000)
    Run() // run 2 seconds
    pause(2000)
    Start() // start 2 seconds
    pause(2000)
    Run() //run
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
def getHemisphere(){
    return [["0":"Northern"],["1":"Southern"]]
}
