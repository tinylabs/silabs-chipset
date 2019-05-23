    #include "target_asm_head.S"
    mov r0, #0
    //  Clear bit0 of MSC to enable bus faults
    ldr r1, =#0x400c0000
    str r0, [r1]
    #include "target_asm_tail.S"
