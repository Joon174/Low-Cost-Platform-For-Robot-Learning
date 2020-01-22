from mujoco_py import load_model_from_xml, MjSim, MjViewer
import math
import os

MODEL_XML= """ 
<?xml version="1.0"	?>
<mujoco model = "Spider Model">
	<default class="main">
		<geom rgba="1 0 0 1"/>
		<default class="sub">
			<geom rgba = "0 1 0 1"/>
		</default>
	</default>
	
	<worldbody>
		<geom type="box"/>
		<body childclass="sub">
			<geom type="ellipsoid"/>
			<geom type="sphere" rgba="0 0 1 0"/>
			<geom type="cylinder" class="main"/>
		</geom>
	</worldbody>
</mujoco>

"""