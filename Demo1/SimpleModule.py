from __future__ import print_function
import os
from __main__ import vtk, qt, ctk, slicer

#
# SlicerLeapModule
#

class SlicerLeapModule(object):
  def __init__(self, parent):
    parent.title = "LeapMotion control"
    parent.categories = ["Gesture control"]
    parent.dependencies = []
    parent.contributors = ["Andras Lasso (PerkLab, Queen's)"]
    parent.helpText = "This is a simple example of interfacing with the LeapMotion controller in 3D Slicer."
    parent.acknowledgementText = ""
    self.parent = parent
    
    # Create the logic to start processing Leap messages on Slicer startup
    logic = SlicerLeapModuleLogic()

#
# qSlicerLeapModuleWidget
#

class SlicerLeapModuleWidget(object):
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Check box to enable creating output transforms automatically.
    # The function is useful for testing and initial creation of the transforms but not recommended when the
    # transforms are already in the scene.
    #
    self.enableAutoCreateTransformsCheckBox = qt.QCheckBox()
    self.enableAutoCreateTransformsCheckBox.checked = 0
    self.enableAutoCreateTransformsCheckBox.setToolTip("If checked, then transforms are created automatically (not recommended when transforms exist in the scene already).")
    parametersFormLayout.addRow("Auto-create transforms", self.enableAutoCreateTransformsCheckBox)
    self.enableAutoCreateTransformsCheckBox.connect('stateChanged(int)', self.setEnableAutoCreateTransforms)

    # Add vertical spacer
    self.layout.addStretch(1)
    
  def cleanup(self):
    pass
  #通过复选框的按钮来执行相关的代码函数，设定自动新建transform函数打开，避免一些错误发生（寻找不到id）
  def setEnableAutoCreateTransforms(self, enable):
    logic = SlicerLeapModuleLogic()
    logic.setEnableAutoCreateTransforms(enable)
  
 

      
      
      
      
# 核心代码在这里
# SlicerLeapModuleLogic
#

class SlicerLeapModuleLogic(object):
  """This class implements all the actual computation in the module.
  """
  
  def __init__(self):
    import Leap
    self.LeapController = Leap.Controller()
    self.enableAutoCreateTransforms = False    
    self.onFrame()  #启动onFrame函数循环，每1s钟10次
      
  def setEnableAutoCreateTransforms(self, enable):
    self.enableAutoCreateTransforms = enable

  def setTransform(self, handIndex, fingerIndex, fingerTipPosition):
    
    transformName = "Hand%iFinger%i" % (handIndex+1,fingerIndex+1) #设定手ID和指头ID
    print('transform:',transformName)
    transform = slicer.util.getNode(transformName)

    # Create the transform if does not exist yet
    if not transform :
      if self.enableAutoCreateTransforms :   #如果复选判断框打开则在次场景中新建一个tranform
        # Create the missing transform
        transform = slicer.vtkMRMLLinearTransformNode()
        transform.SetName(transformName)
        slicer.mrmlScene.AddNode(transform)
      else :
        # No transform exist, so just ignore the finger
        return
    #通过VTK创建一个transform
    newTransform = vtk.vtkTransform()
    # 赋值transform,这里只是赋值给了tranform平移的信息，如果加入旋转的信息也可以在这里，或者缩放的信息
    newTransform.Translate(-fingerTipPosition[0], fingerTipPosition[2], fingerTipPosition[1])
    print('fingerTipPositiion:',fingerTipPosition)  #fingerTipPosition应该是一个坐标，但是也许是一个LPS坐标，所以这里需要转换为RAS坐标
    transform.SetMatrixTransformToParent(newTransform.GetMatrix())
  
  def onFrame(self):
    # Get the most recent frame
    frame = self.LeapController.frame()  #读取LEAP的frame数据
    #迭代每一次的手指的坐标，并且把这个坐标发送给transform
    for handIndex, hand in enumerate(frame.hands) :
      for fingerIndex, finger in enumerate(hand.fingers) :
        self.setTransform(handIndex, fingerIndex, finger.tip_position)
    
    # Theoretically Leap could periodically call a callback function, but due to some reason it does not
    # appear to work, so just poll with a timer instead.
    #通过timer运行单次的迭代,每秒钟迭代10次
    qt.QTimer.singleShot(100, self.onFrame)
