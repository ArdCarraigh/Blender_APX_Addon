templateSimulationMaterial = '''<struct>
            <value name="materialName" type="String">{simulationMaterialName}</value>
            <value name="verticalStretchingStiffness" type="F32">1</value>
            <value name="horizontalStretchingStiffness" type="F32">1</value>
            <value name="bendingStiffness" type="F32">0.5</value>
            <value name="shearingStiffness" type="F32">0.5</value>
            <value name="zeroStretchStiffness" type="F32">0</value>
            <value name="tetherStiffness" type="F32">1</value>
            <value name="tetherLimit" type="F32">1</value>
            <value name="orthoBending" type="Bool">false</value>
            <struct name="verticalStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <struct name="horizontalStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <struct name="bendingStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <struct name="shearingStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <value name="damping" type="F32">0.5</value>
            <value name="stiffnessFrequency" type="F32">100</value>
            <value name="drag" type="F32">0</value>
            <value name="comDamping" type="Bool">false</value>
            <value name="friction" type="F32">0.5</value>
            <value name="massScale" type="F32">25</value>
            <value name="solverIterations" type="U32">5</value>
            <value name="solverFrequency" type="F32">250</value>
            <value name="gravityScale" type="F32">1</value>
            <value name="inertiaScale" type="F32">0.5</value>
            <value name="hardStretchLimitation" type="F32">0</value>
            <value name="maxDistanceBias" type="F32">0</value>
            <value name="hierarchicalSolverIterations" type="U32">0</value>
            <value name="selfcollisionThickness" type="F32">0</value>
            <value name="selfcollisionSquashScale" type="F32">0</value>
            <value name="selfcollisionStiffness" type="F32">0</value>
          </struct>'''