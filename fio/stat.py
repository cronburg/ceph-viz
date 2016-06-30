
FIO_IO_U_PLAT_BITS = 6
FIO_IO_U_PLAT_VAL = (1 << FIO_IO_U_PLAT_BITS)
FIO_IO_U_PLAT_GROUP_NR = 19
FIO_IO_U_PLAT_NR = (FIO_IO_U_PLAT_GROUP_NR * FIO_IO_U_PLAT_VAL)
FIO_IO_U_LIST_MAX_LEN = 20

def plat_idx_to_val(idx):
  # MSB <= (FIO_IO_U_PLAT_BITS-1), cannot be rounded off. Use
  # all bits of the sample as index
  if (idx < (FIO_IO_U_PLAT_VAL << 1)):
    return idx

  # Find the group and compute the minimum value of that group
  error_bits = (idx >> FIO_IO_U_PLAT_BITS) - 1
  base = 1 << (error_bits + FIO_IO_U_PLAT_BITS)

  # Find its bucket number of the group
  k = idx % FIO_IO_U_PLAT_VAL

  # Return the mean of the range of the bucket
  return base + ((k + 0.5) * (1 << error_bits))

def plat_val_to_idx(val):
  # Find MSB starting from bit 0 */
  if (val == 0):
    msb = 0
  else:
    msb = (sizeof(val)*8) - __builtin_clz(val) - 1

  # MSB <= (FIO_IO_U_PLAT_BITS-1), cannot be rounded off. Use
  # all bits of the sample as index
  if (msb <= FIO_IO_U_PLAT_BITS):
    return val
  
  # Compute the number of error bits to discard*/
  error_bits = msb - FIO_IO_U_PLAT_BITS
  
  # Compute the number of buckets before the group */
  base = (error_bits + 1) << FIO_IO_U_PLAT_BITS
  
  # Discard the error bits and apply the mask to find the
  # index for the buckets in the group
  offset = (FIO_IO_U_PLAT_VAL - 1) & (val >> error_bits)
  
  # Make sure the index does not exceed (array size - 1) */
  if ((base + offset) < (FIO_IO_U_PLAT_NR - 1)):
    return (base + offset)
  else:
    return (FIO_IO_U_PLAT_NR - 1)

