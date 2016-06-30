#include <stdio.h>

#define FIO_IO_U_PLAT_BITS 6
#define FIO_IO_U_PLAT_VAL (1 << FIO_IO_U_PLAT_BITS)
#define FIO_IO_U_PLAT_GROUP_NR 19
#define FIO_IO_U_PLAT_NR (FIO_IO_U_PLAT_GROUP_NR * FIO_IO_U_PLAT_VAL)
#define FIO_IO_U_LIST_MAX_LEN 20 /* The size of the default and user-specified
                                              list of percentiles */

static unsigned int plat_val_to_idx(unsigned int val)
{
  unsigned int msb, error_bits, base, offset, idx;

  /* Find MSB starting from bit 0 */
  if (val == 0)
    msb = 0;
  else
    msb = (sizeof(val)*8) - __builtin_clz(val) - 1;

  /*
   * MSB <= (FIO_IO_U_PLAT_BITS-1), cannot be rounded off. Use
   * all bits of the sample as index
   */
  if (msb <= FIO_IO_U_PLAT_BITS)
    return val;
  
  /* Compute the number of error bits to discard*/
  error_bits = msb - FIO_IO_U_PLAT_BITS;
  
  /* Compute the number of buckets before the group */
  base = (error_bits + 1) << FIO_IO_U_PLAT_BITS;
  
  /*
   * Discard the error bits and apply the mask to find the
   * index for the buckets in the group
   */
  offset = (FIO_IO_U_PLAT_VAL - 1) & (val >> error_bits);
  
  /* Make sure the index does not exceed (array size - 1) */
  idx = (base + offset) < (FIO_IO_U_PLAT_NR - 1) ?
    (base + offset) : (FIO_IO_U_PLAT_NR - 1);
  
  return idx;
}

int main(int argc, char *argv[]) {
	for (int i = 0; i < 100000; i++) {
    printf("%lu, ", plat_val_to_idx(i));
  }  
}

