class AR():
  
  total_height = 120
  total_width = 160
  total_treshold = 50

  ker_n = 3
  ker_ul = [[ 1, 1, 1],
            [ 1, 0,-2],
            [ 1,-2,-2]]

  ker_ur = [[ 1, 1, 1],
            [-2, 0, 1],
            [-2,-2, 1]]

  ker_ll = [[ 1,-2,-2],
            [ 1, 0,-2],
            [ 1, 1, 1]]

  ker_lr = [[-2,-2, 1],
            [-2, 0, 1],
            [ 1, 1, 1]]
       
       
  def convolution(img, ker):
    points = []
    for i in range(total_height - ker_n + 1):
      for j in range(total_width - ker_n + 1):
        s = 0
        for k in range(ker_n):
          s += ker[k][0] * img[i+k][j] + ker[k][1] * img[i + k][j + 1] + ker[k][2] * img[i + k][j + 2]
        if s == 255 * 5:
          points.append((i, j))
    return points

    
  def grayScale(sPic):
    bufPic = [];
    for i in range(total_height):
      for j in range(total_width):
        x = i * total_width + j
        p = sPic[x]
        r = (p & 0xff0000) >> 16	# взять значение компоненты красного
        g = (p & 0xff00) >> 8 # взять значение компоненты зеленого
        b = (p & 0xff) # взять значение компоненты синего
        p = r * 0.299 + g * 0.587 + b * 0.114 # компонента Y из YUV
        bufPic.append(p)
    return bufPic


  # Бинаризация -- перевод изображения в ЧБ
  def binarization(treshold, sPic):
    bufPic = []
    for i in range(len(sPic)):
      bufPic.append(255 if sPic[i] > treshold else 0);
    return bufPic;
    

  def flat_to_matrix(img):
    mat = [[0] * total_width for i in range(total_height)]
    for i in range(total_height):
      for j in range(total_width):
        mat[i][j] = img[i * total_width + j]
    return mat
    
    
  def matrix_to_flat(mat):
    output = []
    for i in range(total_height):
      for j in range(total_width):
        output.append(mat[i][j])
    return output


  def find_vertices(Mat):
    p = convolution(Mat, ker_ul)
    ul = Argmin(p, lambda x: x[0] + x[1])
    
    p = convolution(Mat, ker_ur)
    ur = Argmax(p, lambda x: x[1])
    
    p = convolution(Mat, ker_ll)
    ll = Argmin(p, lambda x: x[1])

    p = convolution(Mat, ker_lr)
    lr = Argmax(p, lambda x: x[0] + x[1])
    
#    print(ul, ur, ll, lr)
    return (ul, ur, ll, lr)


  def Argmin(collection, func):
    m = 1e10
    I = ()
    for i in collection:
      if func(i) < m:
        I = i
        m = func(i)
    return I
    
  def Argmax(collection, func):
    m = -1e10
    I = ()
    for i in collection:
      if func(i) > m:
        I = i
        m = func(i)
    return I
    
  def reduce(Mat, o_array, sx, sy, dx, dy):
    flag = True
    tag = [[-1] * 5 for i in range(5)]
    for i in range(5):
      for j in range(5):
        tag[j][i] = Mat[int(sx + i * dx[0] + j * dy[0])][int(sy + i * dx[1] + j * dy[1])] // 255
        if (i == 0 or j == 0) and tag[j][i] != 0:
          flag = False
    if flag and (tag[1][1] + tag[1][3] + tag[3][1] + tag[3][3] == 1):
      o_array.append(tag)
  
  def make_tag_matrix(Mat, vertices):
    (ul, ur, ll, lr) = vertices
    tags = []
    
    if len(ul) > 0 and len(ur) > 0 and len(ll) > 0:
      dx = (ur[0] - ul[0]) / 5, (ur[1] - ul[1]) / 5
      dy = (ll[0] - ul[0]) / 5, (ll[1] - ul[1]) / 5
      sx, sy = ul[0] + dx[0]/2 + dy[0]/2, ul[1] + dx[1]/2 + dy[1]/2
      AR.reduce(Mat, tags, sx, sy, dx, dy)
     
    if len(ul) > 0 and len(ur) > 0 and len(lr) > 0:
      dx = (ur[0] - ul[0]) / 5, (ur[1] - ul[1]) / 5
      dy = (lr[0] - ur[0]) / 5, (lr[1] - ur[1]) / 5 
      sx, sy = ul[0] + dx[0]/2 + dy[0]/2, ul[1] + dx[1]/2 + dy[1]/2
      AR.reduce(Mat, tags, sx, sy, dx, dy)
            
    if len(lr) > 0 and len(ur) > 0 and len(ll) > 0:
      dx = (lr[0] - ll[0]) / 5, (lr[1] - ll[1]) / 5
      dy = (lr[0] - ur[0]) / 5, (lr[1] - ur[1]) / 5
      sx, sy = lr[0] - 4.5 * (dx[0] + dy[0]), lr[1] - 4.5 * (dx[1] + dy[1])
      AR.reduce(Mat, tags, sx, sy, dx, dy)
    
    if len(ul) > 0 and len(ll) > 0 and len(lr) > 0:
      dx = (lr[0] - ll[0]) / 5, (lr[1] - ll[1]) / 5
      dy = (ll[0] - ul[0]) / 5, (ll[1] - ul[1]) / 5
      sx, sy = ul[0] + dx[0]/2 + dy[0]/2, ul[1] + dx[1]/2 + dy[1]/2
      AR.reduce(Mat, tags, sx, sy, dx, dy)
      
    return tags


  def decode(tag):
    t = (tag[1][2] + tag[2][1] + tag[3][2] + tag[2][3] + tag[2][2])
    if t % 2 != 1:
      print("checksum doesn't match")
    s = ""
    if tag[3][3] == 1:
      s = str(tag[1][2]) + str(tag[2][1]) + str(tag[2][3]) + str(tag[3][2])
    elif tag[3][1] == 1:
      s = str(tag[2][3]) + str(tag[1][2]) + str(tag[3][2]) + str(tag[2][1]) 
    elif tag[1][1] == 1:
      s = str(tag[3][2]) + str(tag[2][3]) + str(tag[2][1]) + str(tag[1][2]) 
    elif tag[1][3] == 1:
      s = str(tag[2][1]) + str(tag[3][2]) + str(tag[1][2]) + str(tag[2][3])  
      
    # инвертирование бит перевод числа из двоичного в десятичный формат
    num = int(s, 2)
    num = ~num + 16
    
    return num
  
    
  def get_and_decode_tag():
    # взять кадр в формате rgb32
    pic = getPhoto();
    brick.display().show(pic, total_width, total_height, "rgb32");

    pic = AR.grayScale(pic)
    pic = AR.binarization(total_treshold, pic)

    Mat = AR.flat_to_matrix(pic)
    (ul, ur, ll, lr) = AR.find_vertices(Mat)
    tags = AR.make_tag_matrix(Mat, (ul, ur, ll, lr))
    d = {}
    for tag in tags:
      c = AR.decode(tag)
      try:
        d[c] += 1
      except:
        d[c] = 1
    m = 0
    cipher = 0
    for i in d:
      if d[i] > m:
        cipher = i
        m = d[i]
    print(cipher)
 

if __name__ == "__main__":
  ar = AR()
  for i in range(11):
      AR.get_and_decode_tag()
      

