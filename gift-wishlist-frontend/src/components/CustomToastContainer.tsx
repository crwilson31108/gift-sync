import { createStandaloneToast } from '@chakra-ui/react';
import { css, Global } from '@emotion/react';

export const CustomToastContainer = () => {
  return (
    <Global
      styles={css`
        .chakra-toast-container {
          z-index: 10000 !important;
        }
      `}
    />
  );
}; 