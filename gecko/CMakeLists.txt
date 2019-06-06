# Gecko chipset config
set_prop( BOOT_PAGE_SIZE 512 )
leos_include( core.map /cfg )
leos_include( irq.map /cfg )
leos_include( periph.map /cfg )

# Include boot dependency
add_component ( boot/gecko-boot )

# Include chipset debug info
include ( ./chipset-gdb.cmake )

