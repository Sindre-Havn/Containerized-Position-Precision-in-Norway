import { atom } from 'jotai'

export const updateDataState = atom(false)

export const timeState = atom(new Date())

export const epochState = atom(1)
export const elevationState = atom(10)

export const endPointsState = atom([])

export const vegReferanseState = atom('EV136')
export const startPointState = atom([136149.75, 6941757.94])
export const endPointState = atom([193547.58,6896803.47])
export const distanceState = atom(10000)

export const roadState = atom(false)

export const pointsState = atom([])

export const updateDOPState = atom(false)

export const gnssState = atom({
    GPS: true,
    GLONASS: true,
    Galileo: true,
    BeiDou: true,
    QZSS: true,
    NavIC: false,
  
  })

export const gnssState2 = atom({
    GPS: true,
    GLONASS: true,
    Galileo: true,
    BeiDou: true,
    QZSS: true,
    NavIC: false,

  })