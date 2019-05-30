    //  Clear bit0 of MSC to enable bus faults
    mov r0, #0
    ldr r1, =#0x400c0000
    str r0, [r1]
