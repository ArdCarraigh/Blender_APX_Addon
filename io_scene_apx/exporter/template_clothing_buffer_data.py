templateDataPositionNormal = '''<value type="Ref" included="1" className="BufferF32x3" version="0.0" checksum="0x458b554a 0x7ed3e930 0x299ff33 0x9d69c11b">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Vec3">
	                            {arrayData}
                              </array>
                            </struct>
                          </value>'''
templateDataTangent = '''<value type="Ref" included="1" className="BufferF32x4" version="0.1" checksum="0x80321851 0xa99e95a1 0xd26ec9a8 0x14206b37">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(F32),y(F32),z(F32),w(F32)">
	                            {arrayData}
                              </array>
                            </struct>
                          </value>'''
templateDataColor = '''<value type="Ref" included="1" className="BufferU8x4" version="0.0" checksum="0x8364dd0f 0xbc7542d0 0x1a22d2d2 0x1fc1923">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(U8),y(U8),z(U8),w(U8)">
	                            {arrayData}
                              </array>
                            </struct>
                          </value>'''
templateDataUV = '''<value type="Ref" included="1" className="BufferF32x2" version="0.0" checksum="0x788349ee 0x95c560e2 0x9633945e 0x8cc784a0">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(F32),y(F32)">
	                            {arrayData}
                              </array>
                            </struct>
                          </value>'''
templateDataBoneIndex = '''<value type="Ref" included="1" className="BufferU16x4" version="0.0" checksum="0x17ce6b83 0x32ba98aa 0xd03f98f6 0x26918369">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(U16),y(U16),z(U16),w(U16)">
	                            {arrayData}
                              </array>
                            </struct>
                          </value>'''
templateDataBoneWeight = '''<value type="Ref" included="1" className="BufferF32x4" version="0.1" checksum="0x80321851 0xa99e95a1 0xd26ec9a8 0x14206b37">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(F32),y(F32),z(F32),w(F32)">
	                            {arrayData}
                              </array>
                            </struct>
                          </value>'''