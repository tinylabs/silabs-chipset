# Silabs chipset config
leos_fs( core.map /cfg )
leos_fs( irq.map /cfg )
leos_fs( periph.map /cfg )
leos_fs( driver.map /cfg )
leos_clock_tree( clock.tree /cfg )

# Include generated dependencies
include( ./auto.cmake )
