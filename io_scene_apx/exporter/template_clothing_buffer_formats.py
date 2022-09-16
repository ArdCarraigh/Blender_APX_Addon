templateVertexPositionBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_POSITION</value>
                                <value name="semantic" type="I32">0</value>
                                <value name="id" type="U32">4058349641</value>
                                <value name="format" type="U32">43</value>
                                <value name="access" type="U32">1</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
templateVertexNormalBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_NORMAL</value>
                                <value name="semantic" type="I32">1</value>
                                <value name="id" type="U32">628990755</value>
                                <value name="format" type="U32">43</value>
                                <value name="access" type="U32">1</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
templateVertexTangentBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_TANGENT</value>
                                <value name="semantic" type="I32">2</value>
                                <value name="id" type="U32">1201849363</value>
                                <value name="format" type="U32">44</value>
                                <value name="access" type="U32">1</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
templateVertexColorBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_COLOR</value>
                                <value name="semantic" type="I32">4</value>
                                <value name="id" type="U32">3000270285</value>
                                <value name="format" type="U32">17</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
templateVertexUVBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_TEXCOORD{numUVBuffer}</value>
                                <value name="semantic" type="I32">{semanticUVBuffer}</value>
                                <value name="id" type="U32">122905935{idEndUVBuffer}</value>
                                <value name="format" type="U32">42</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
templateVertexBoneIndexBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_BONE_INDEX</value>
                                <value name="semantic" type="I32">9</value>
                                <value name="id" type="U32">284127831</value>
                                <value name="format" type="U32">8</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
templateVertexBoneWeightBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_BONE_WEIGHT</value>
                                <value name="semantic" type="I32">10</value>
                                <value name="id" type="U32">2091801033</value>
                                <value name="format" type="U32">44</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''