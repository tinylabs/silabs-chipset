# Silabs chipset config
include( ./auto.cmake )
leos_include( core.map /cfg )
leos_include( irq.map /cfg )
leos_include( periph.map /cfg )
leos_include( driver.map /cfg )
leos_clock_tree( clock.tree /cfg )
