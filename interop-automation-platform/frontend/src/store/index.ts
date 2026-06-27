// index
import { configureStore } from '@reduxjs/toolkit';
import fhirValidatorReducer from './fhirValidatorSlice';

export const store = configureStore({
  reducer: {
    fhirValidator: fhirValidatorReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
