# Gecko chipset config
set_prop( BOOT_PAGE_SIZE 512 )
leos_include( core.map /cfg )
leos_include( irq.map /cfg )
leos_include( periph.map /cfg )

# Include boot dependency
add_component ( boot/gecko_boot )
