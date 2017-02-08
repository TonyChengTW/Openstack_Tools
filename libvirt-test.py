import libvirt
con = libvirt.openReadOnly('qemu:///system')
dom = con.lookupByUUIDString('f47ccc3a-6c9d-471d-bcb0-0781ab54a71f')
print dom.memoryStats()
