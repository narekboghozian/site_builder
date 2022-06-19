import xml.etree.cElementTree as ET

Generate JSON for


rss = ET.Element("rss")
channel = ET.SubElement(root, "channel")

ET.SubElement(channel, "field1", name="blah").text = "some value1"
ET.SubElement(channel, "field2", name="asdfasd").text = "some vlaue2"

tree = ET.ElementTree(root)
tree.write("filename.xml")
