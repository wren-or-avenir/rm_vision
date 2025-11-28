import cv2
import numpy as np
from pprint import pprint

#这个图像的展示窗口后续需要再调整一下，可以多窗口同时展示二值化后的图像，最小外接轮廓检测结果，等
#目前先实现单窗口展示
def show_image(img):

    h, w = img.shape[:2]
    max_display_size = 800

    if max(h, w) > max_display_size:
        scale = max_display_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    

    cv2.imshow("detector2",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 灰度化，二值化预处理 # val原先设置为140
def preprocessing(img,val):

    # img_resized = cv2.resize(img, (640, 480))
    img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    retval, result = cv2.threshold(img_gray, val, 255, cv2.THRESH_BINARY)
    return result

# 轮廓检测并绘制外轮廓
def detect_contours(img, color_img):

    contours, hierarchy = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    result_img = color_img.copy()   #转为彩色图用于绘制
    cv2.drawContours(result_img, contours,  -1, (0, 255, 0), 2)
    return result_img

# 绘制灯带最小外接矩形，用面积做初筛
def draw_min_rect(img, color_img, target_color1_range = None, target_color2_range = None):
    
    contours, _ = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    result_img = color_img.copy()   #转为彩色图用于绘制
    rect_info_list = []     # 用于存储矩形信息的列表
    
    if contours is None:
        return None, None
    
    for contour in contours:
        if len(contour) >= 3:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.intp(box)     
            width = rect[1][0]
            height = rect[1][1]
            area = cv2.contourArea(contour)

            if  40<=area:   # 面积初筛

                cv2.drawContours(result_img, [box], 0, (0, 255, 0), 1)

                # 绘制最小外接矩形的中心点
                center_x, center_y = int(rect[0][0]), int(rect[0][1])
                cv2.circle(result_img, (center_x, center_y), 1, (0, 0, 255), -1)  # 红色圆点
                
                # 标出中心坐标文字
                cv2.putText(result_img, f'({center_x}, {center_y})', 
                           (center_x + 10, center_y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
                # 存储矩形信息
                rect_info_list.append({
                    'box': box,
                    'width': width,
                    'height': height,
                    'area': area,
                    'center': rect[0],
                    'angle': rect[2]
                })
    return result_img, rect_info_list

# 调整矩形参数，使宽为较长边，角度调整到0-90度之间
def adjust(rect):
    width = rect[1][0]
    height = rect[1][1]
    angle = rect[2]

    w = width
    h = height
    temp = 0

    if h<w:
        temp = h
        h = w
        w = temp
        if angle == 0:
            angle += 90
            return w,h,angle
        angle -= 90
        angle = abs(angle)
        return w,h,angle
    if w<h:
        if angle > 90:
            angle -= 90
        return w,h,angle

# 根据长宽比和角度筛选矩形，并绘制筛选结果
def filter_by_ratio_and_angle_with_adjust(color_img, rect_info_list):

    result_img = color_img.copy()
    filtered_rects = []
    
    for rect_info in rect_info_list:
        # 使用adjust函数调整矩形参数
        original_rect = ((rect_info['center'][0], rect_info['center'][1]), 
                        (rect_info['width'], rect_info['height']), 
                        rect_info['angle'])
        
        adjusted_w, adjusted_h, adjusted_angle = adjust(original_rect)
        
        # 计算长宽比（较长边/较短边） # w除零保护
        ratio = adjusted_h / adjusted_w if adjusted_w != 0 else float('inf')
        
        # 长宽比筛选：3到7之间
        # 角度筛选：-30到30度之间
        # 其实基于我的思路，我将角度都调整到了正值范围内，所以这里可以直接用0到30度之间筛选
        if 3 <= ratio <= 8 and -30 <= adjusted_angle <= 30:
            # 绘制符合条件的矩形
            box = rect_info['box']
            cv2.drawContours(result_img, [box], 0, (0, 255, 0), 2)  # 用绿色绘制筛选后的矩形

            # 绘制最小外接矩形的中心点
            center_x, center_y = int(rect_info['center'][0]), int(rect_info['center'][1])
            cv2.circle(result_img, (center_x, center_y), 3, (0, 0, 255), -1)  # 红色圆点
            
            # 标出中心坐标文字
            cv2.putText(result_img, f'({center_x}, {center_y})', 
                       (center_x + 10, center_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 存储筛选后的矩形信息
            filtered_rects.append({
                'box': box,
                'width': rect_info['width'],
                'height': rect_info['height'],
                'area': rect_info['area'],
                'center': rect_info['center'],
                'angle': rect_info['angle'],
                'adjusted_width': adjusted_w,
                'adjusted_height': adjusted_h,
                'adjusted_angle': adjusted_angle
            })
    
    return result_img, filtered_rects 

# 接下来配对每组灯带，进行匹配    
def is_close(rect1,rect2):
    (x1,y1),(w1,h1),angle1 = rect1
    (x2,y2),(w2,h2),angle2 = rect2
    # 使用adjust函数调整矩形参数
    adjusted_w1, adjusted_h1, adjusted_angle1 = adjust(((x1, y1), (w1, h1), angle1))
    adjusted_w2, adjusted_h2, adjusted_angle2 = adjust(((x2, y2), (w2, h2), angle2))
    
    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    #利用angle1得到矩形1的斜率s1
    s1 = np.tan(np.deg2rad(adjusted_angle1))       
    #利用angle2得到矩形2的斜率s2
    s2 = np.tan(np.deg2rad(adjusted_angle2))
    #计算两点连线的斜率s3 
        # w除零保护
    if (x1 - x2) != 0 :
        s3 = (y1 - y2) / (x1 - x2)
    else :
        s3 = float('inf')
    
    #取较短边作为h
    min_h = min(adjusted_h1,adjusted_h2)
    max_h = max(adjusted_h1,adjusted_h2)

    #情况一：远
    # 如果两点y坐标差值小于1，认为是同一组灯条，直接返回True
    far_parmas = 4
    if abs(y2 - y1)< 2:
        if min_h* far_parmas < distance < max_h* far_parmas:
            return True
        else:
            return False

    #情况二：近    
    #对 if abs(s1* s3 + 1) == 0 or abs(s2* s3 + 1) ==0 进行优化
    near_parmas = 2
    if abs(s1* s3 + 1)< 0.3 or abs(s2* s3 + 1) <0.3:
        if min_h* near_parmas < distance < max_h* near_parmas:
            return True
        else:
            return False

#画出经过配对的灯条，绘制每组中点连线，连接每组的中点，并标注连线中点坐标
def draw_paired_lights(color_img, filtered_rects):
    """
    根据配对条件筛选并绘制配对的灯条
    """
    result_img = color_img.copy()
    paired_groups = []  # 存储配对的灯条组
    
    # 获取所有符合条件的矩形
    rect_list = []
    for rect_info in filtered_rects:
        original_rect = ((rect_info['center'][0], rect_info['center'][1]), 
                        (rect_info['width'], rect_info['height']), 
                        rect_info['angle'])
        rect_list.append(original_rect)
    
    # 遍历所有矩形对进行配对
    processed_indices = set()
    for i in range(len(rect_list)):
        if i in processed_indices:
            continue
            
        current_group = [rect_list[i]]
        current_center = rect_list[i][0]  # (x, y)
        
        # 寻找与当前矩形配对的其他矩形
        for j in range(i + 1, len(rect_list)):
            if j in processed_indices:
                continue
                
            if is_close(rect_list[i], rect_list[j]):
                current_group.append(rect_list[j])
                processed_indices.add(j)
        
        if len(current_group) >= 2:  # 至少配对成功2个
            paired_groups.append(current_group)
            processed_indices.add(i)
    
    # 绘制配对的灯条和连线
    for group in paired_groups:
        centers = []
        for rect in group:
            center = rect[0]  # (x, y)
            centers.append(center)
            
            # 绘制单个矩形
            box = cv2.boxPoints(rect).astype(int)
            cv2.drawContours(result_img, [box], 0, (0, 255, 0), 7)
        
        # 绘制中心点连线和中点
        if len(centers) >= 2:
            for i in range(len(centers)):
                for j in range(i + 1, len(centers)):
                    pt1 = (int(centers[i][0]), int(centers[i][1]))
                    pt2 = (int(centers[j][0]), int(centers[j][1]))
                    
                    # 绘制连线
                    cv2.line(result_img, pt1, pt2, (255, 0, 0), 5)
                    
                    # 计算并绘制中点
                    mid_x = (pt1[0] + pt2[0]) // 2
                    mid_y = (pt1[1] + pt2[1]) // 2
                    mid_point = (mid_x, mid_y)
                    
                    cv2.circle(result_img, mid_point, 7, (0, 0, 255), -1)  # 绘制中点
                    
                    # 标注中点坐标
                    coord_text = f"({mid_x}, {mid_y})"
                    cv2.putText(result_img, coord_text, (mid_x + 10, mid_y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 5)

    return result_img, paired_groups


if __name__ == "__main__":
    
    #读取图片文件
    path = 'D:/Avenir/Pictures/homework3/detector2.png'      
    original_img = cv2.imread(path)  
    # original_img = cv2.flip(original_img,1)   #上下翻转
    original_img = cv2.resize(original_img, (640, 480))
    #显示原图
    show_image(original_img)                            

    #轮廓检测前的预处理
    preprocessed_img = preprocessing(original_img,140)
    show_image(preprocessed_img) 

    #轮廓检测并绘制外轮廓
    detected_contours = detect_contours(preprocessed_img, original_img)
    show_image(detected_contours)
    #绘制最小外接矩形并做面积初筛
    drawn_min_rect_img ,rect_info_list= draw_min_rect(preprocessed_img, original_img)
    show_image(drawn_min_rect_img)

    # # 可以打印矩形信息
    # print("检测到的矩形数量:", len(rect_info_list))
    # pprint(rect_info_list)

    # 根据长宽比和角度筛选矩形，并绘制筛选结果
    filtered_img, filtered_rects = filter_by_ratio_and_angle_with_adjust(original_img, rect_info_list)
    show_image(filtered_img)
    
    # 打印筛选后的矩形信息
    print("经过adjust调整和长宽比角度筛选后的矩形数量:", len(filtered_rects))
    pprint(filtered_rects)

    # 绘制配对的灯条
    paired_img, paired_groups = draw_paired_lights(original_img, filtered_rects)
    show_image(paired_img)
    
    print("配对成功的组数:", len(paired_groups))
    for i, group in enumerate(paired_groups):
        print(f"第{i+1}组配对的矩形数量: {len(group)}")