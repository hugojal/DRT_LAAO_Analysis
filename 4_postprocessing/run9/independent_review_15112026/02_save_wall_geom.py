# pvbatch: save la_wall surface (t=2.63) and fluid surface geometry for connectivity
from paraview.simple import *
ROOT=r'C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3'
r=EnSightReader(CaseFileName=ROOT+'/6_paraview_package/simulation/run9_last_beat.encas')
wl=ExtractBlock(Input=r); wl.Selectors=['/Root/la_wall']
m=MergeBlocks(Input=wl); s=ExtractSurface(Input=m)
SaveData(ROOT+'/4_postprocessing/run9/independent_review_15112026/cache/la_wall_t2.63.vtp', proxy=s)
